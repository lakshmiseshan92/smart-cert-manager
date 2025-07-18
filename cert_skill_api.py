from flask import Flask, request, jsonify, send_file
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
import os
import json

app = Flask(__name__)

BASE_DIR = os.path.dirname(__file__)
CERTS_FILE = os.path.join(BASE_DIR, "certs.json")
LOG_FILE = os.environ.get("RENEW_LOG_PATH", os.path.join(BASE_DIR, "renew_log.json"))

@app.route("/")
def home():
    return "SmartCert Flask API running."

@app.route("/renew", methods=["POST"])
def renew_cert():
    try:
        data = request.get_json()
        host = data.get("host")
        mock = data.get("mock", True)

        if not host:
            return jsonify({"success": False, "output": "host is required"}), 400

        certs = []
        if os.path.exists(CERTS_FILE):
            with open(CERTS_FILE, "r") as f:
                certs = json.load(f)

        for cert in certs:
            if cert.get("host") == host:
                cert["mock_expiry"] = (datetime.utcnow() + timedelta(days=90)).strftime("%b %d %H:%M:%S %Y GMT")

        with open(CERTS_FILE, "w") as f:
            json.dump(certs, f, indent=2)

        renew_log = {}
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as f:
                renew_log = json.load(f)

        renew_log[host] = datetime.utcnow().isoformat() + "Z"

        with open(LOG_FILE, "w") as f:
            json.dump(renew_log, f, indent=2)

        return jsonify({
            "domain": host,
            "success": True,
            "output": f"[MOCK] Renewal recorded for {host}",
            "mode": "MOCK" if mock else "REAL"
        })

    except Exception as e:
        return jsonify({"success": False, "output": f"Error: {str(e)}"}), 500

@app.route("/log", methods=["GET"])
def get_log():
    try:
        with open(LOG_FILE, "r") as f:
            log = json.load(f)
        return jsonify({"success": True, "log": log})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/export/pdf-link", methods=["GET"])
def export_pdf_link():
    return jsonify({
        "success": True,
        "download_link": "https://smart-cert-manager.onrender.com/export/pdf-file"
    })

@app.route("/export/pdf-file", methods=["GET"])
def export_pdf_file():
    try:
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        c.setFont("Helvetica", 12)
        c.drawString(100, 750, "SmartCert Certificate Report")

        if os.path.exists(CERTS_FILE):
            with open(CERTS_FILE, "r") as f:
                certs = json.load(f)
        else:
            certs = []

        y = 720
        for cert in certs:
            line = f"{cert['host']} - Expires: {cert.get('mock_expiry', 'unknown')}"
            c.drawString(100, y, line)
            y -= 20

        c.save()
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name="cert_report.pdf", mimetype="application/pdf")

    except Exception as e:
        return jsonify({"success": False, "output": f"Failed to generate PDF: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
