import streamlit as st
import json
from datetime import datetime
from cert_renewer import renew_with_certbot
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import threading
import time

st.set_page_config(layout="wide")

CERTS_FILE = "certs.json"
LOG_FILE = "renewal_log.json"
AUTO_RENEW_INTERVAL = 60
AUTO_RENEW_THRESHOLD_MINUTES = 5

# Sidebar settings
st.sidebar.title("⚙️ Settings")
mock_mode = st.sidebar.radio("Renewal Mode", ["Mock", "Real"]) == "Mock"
enable_real_auto = st.sidebar.checkbox("Enable Real Certbot Auto-Renew", value=False)
export_pdf = st.sidebar.button("📄 Export to PDF")

# Load certs
with open(CERTS_FILE, "r") as f:
    certs = json.load(f)

# Load or init renewal log
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as f:
        json.dump({}, f)

with open(LOG_FILE, "r") as f:
    renewal_log = json.load(f)

# Auto-renewal background loop
def auto_renew_loop():
    while True:
        try:
            with open(CERTS_FILE, "r") as f:
                certs = json.load(f)
            now = datetime.utcnow()
            updated = False
            for cert in certs:
                expiry_str = cert.get("mock_expiry")
                if not expiry_str:
                    continue
                try:
                    expiry = datetime.strptime(expiry_str, "%b %d %H:%M:%S %Y GMT")
                    time_left = (expiry - now).total_seconds() / 60
                    if 0 <= time_left <= AUTO_RENEW_THRESHOLD_MINUTES:
                        is_mock = mock_mode or not enable_real_auto
                        result = renew_with_certbot(cert["host"], mock_mode=is_mock)
                        renewal_log[cert["host"]] = datetime.utcnow().isoformat()
                        with open(LOG_FILE, "w") as logf:
                            json.dump(renewal_log, logf, indent=2)
                        print(f"[AUTO] {result['output']}")
                        updated = True
                except Exception as e:
                    print(f"[AUTO] Error: {e}")
            time.sleep(AUTO_RENEW_INTERVAL)
        except Exception as e:
            print(f"[AUTO LOOP ERROR]: {e}")
            time.sleep(60)

threading.Thread(target=auto_renew_loop, daemon=True).start()

# PDF Export logic
def export_to_pdf(certs):
    pdf_path = "certificate_report.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.setFont("Helvetica", 12)
    y = 750
    c.drawString(100, y, "Certificate Expiry Report")
    y -= 30
    for cert in certs:
        line = f"{cert['name']} ({cert['host']}) - Expires on {cert['mock_expiry']}"
        c.drawString(80, y, line)
        y -= 20
    c.save()
    return pdf_path

if export_pdf:
    path = export_to_pdf(certs)
    with open(path, "rb") as f:
        st.sidebar.download_button("Download PDF", f, file_name="certificate_report.pdf")

# Cert dashboard
st.title("📋 Certificate Expiry Status")
for cert in certs:
    expiry = cert.get("mock_expiry")
    exp_dt = datetime.strptime(expiry, "%b %d %H:%M:%S %Y GMT")
    days_left = (exp_dt - datetime.utcnow()).days
    last_renewed = renewal_log.get(cert["host"], "—")
    col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 3])
    with col1:
        st.write(f"**{cert['name']}** ({cert['host']})")
    with col2:
        st.write(f"🗓️ `{expiry}`")
    with col3:
        status = "🟢" if days_left > 7 else "🟡" if days_left > 1 else "🔴"
        st.write(f"{status} In {days_left} day(s)")
    with col4:
        if st.button(f"Renew {cert['host']}", key=cert['host']):
            result = renew_with_certbot(cert["host"], mock_mode=mock_mode)
            if result["success"]:
                renewal_log[cert["host"]] = datetime.utcnow().isoformat()
                with open(LOG_FILE, "w") as logf:
                    json.dump(renewal_log, logf, indent=2)
                st.success(f"✅ {result['output']}")
                if result["mode"] == "REAL":
                    st.info(f"🛠️ Real certbot output:\n\n{result['output']}")
                st.rerun()
            else:
                st.error(f"❌ Renewal failed: {result['output']}")
                if result["mode"] == "REAL":
                    st.error(f"❌ Certbot output:\n\n{result['output']}")
    with col5:
        st.write(f"🕓 Last Renewed: `{last_renewed}`")