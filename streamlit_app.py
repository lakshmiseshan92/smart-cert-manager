import streamlit as st
import json
import requests
from datetime import datetime
import os
from streamlit_autorefresh import st_autorefresh


st.set_page_config(layout="wide")
st.title("📋 Smart Certificate Dashboard")

CERTS_FILE = "certs.json"
REMOTE_LOG_URL = "https://smart-cert-manager.onrender.com/log"

# Auto-refresh every 5 seconds
# st.experimental_rerun_interval = 5000
st_autorefresh(interval=5000, limit=None, key="refresh")


# Load certificate data
if os.path.exists(CERTS_FILE):
    with open(CERTS_FILE, "r") as f:
        certs = json.load(f)
else:
    certs = []

# Fetch renewal log remotely
try:
    response = requests.get(REMOTE_LOG_URL)
    if response.status_code == 200:
        renew_log = response.json().get("log", {})
    else:
        renew_log = {}
        st.error("Failed to fetch log from API.")
except Exception as e:
    renew_log = {}
    st.error(f"Error fetching renewal log: {str(e)}")

st.subheader("🔐 Certificates Overview")
for cert in certs:
    host = cert.get("host", "unknown")
    expiry = cert.get("mock_expiry", "unknown")
    last_renewed = renew_log.get(host, "—")

    st.markdown(f"""
        **🔐 Host**: `{host}`  
        🗓️ **Expires On**: `{expiry}`  
        🔄 **Last Renewed**: `{last_renewed}`  
        ---
        """)

st.info("This dashboard auto-refreshes every 5 seconds and reads the latest renewal log from the Flask API.")
