from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__)

LOG_FILE = os.environ.get("RENEW_LOG_PATH", "/tmp/renew_log.json")
CERTS_FILE = os.environ.get("CERTS_PATH", os.path.join(os.path.dirname(__file__), "certs.json"))

# 🔍 Debug output for Render logs
print(f"🛠 Writing log to: {LOG_FILE}")
print(f"📘 Reading certs from: {CERTS_FILE}")

@app.route("/renew", methods=["POST"])
def renew_cert():
    try:
        data = request.get_json()
        host = data.get("host")
        mock = data.get("mock", True)

        if not host:
            return jsonify({"success": False, "output": "host is required"}), 400

        # Load certs.json
        certs = []
        if os.path.exists(CERTS_FILE):
            with open(CERTS_FILE, "r") as f:
                certs = json.load(f)

        # Update expiry if host found
        updated = False
        for cert in certs:
            if cert.get("host") == host:
                cert["mock_expiry"] = (datetime.utcnow() + timedelta(days=90)).strftime("%b %d %H:%M:%S %Y GMT")
                updated = True

        # Save updated certs file
        with open(CERTS_FILE, "w") as f:
            json.dump(certs, f, indent=2)

        # Always update renew_log.json
        renew_log = {}
        try:
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, "r") as f:
                    renew_log = json.load(f)
        except Exception as e:
            print(f"⚠️ Failed to read existing log: {e}")

        # Always log the renewal attempt
        renew_log[host] = datetime.utcnow().isoformat() + "Z"

        try:
            with open(LOG_FILE, "w") as f:
                json.dump(renew_log, f, indent=2)
            print(f"✅ Logged renewal for {host}")
        except Exception as e:
            print(f"❌ Failed to write log: {e}")
        
        print(f"✅ Updated renew_log.json with {host} at {renew_log[host]}")

        return jsonify({
            "domain": host,
            "success": True,
            "output": f"[MOCK] {'Updated' if updated else 'Logged only'} for {host}",
            "mode": "MOCK" if mock else "REAL"
        })

    except Exception as e:
        return jsonify({"success": False, "output": f"Error: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
