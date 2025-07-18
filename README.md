![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/streamlit-dashboard-orange)
![License](https://img.shields.io/badge/license-MIT-green)
![Auto-Renew](https://img.shields.io/badge/auto--renew-enabled-success)

# 🔐 Smart Certificate Manager

This project provides a mock/real certificate expiry and renewal dashboard with:
- 🟢 Auto-renewal for soon-to-expire and expired certificates
- 📊 Streamlit dashboard with live status, PDF export, and renewal buttons
- 🔁 Mock mode for safe simulation
- 🛠️ Real mode with Certbot integration (optional)

## 🚀 Getting Started

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## 📁 Files

- `streamlit_app.py` - Main Streamlit dashboard
- `cert_renewer.py` - Renewal logic
- `certs.json` - Mock cert data
- `renewal_log.json` - Auto-renewal logs

## ⚙️ Features
- Auto-renew expired certs ✅
- Mock mode + real mode toggle ✅
- Export PDF report ✅
- Real certbot integration (optional) ✅
