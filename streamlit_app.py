import streamlit as st
import json
from datetime import datetime
import os

st.set_page_config(layout="wide")
st.title("📋 Smart Certificate Dashboard")

CERTS_FILE = "certs.json"
LOG_FILE = "renew_log.json"

# Auto-refresh every 5 seconds
st.experimental_rerun_interval = 5000

# Load certificate data
if os.path.exists(CERTS_FILE):
    with open(CERTS_FILE, "r") as f:
        certs = json.load(f)
else:
    certs = []

# Load renewal log
if os.path.exists(LOG_FILE):
    with open(LOG_FILE, "r") as f:
        renew_log = json.load(f)
else:
    renew_log = {}

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

st.info("This dashboard auto-refreshes every 5 seconds to reflect certificate updates.")
