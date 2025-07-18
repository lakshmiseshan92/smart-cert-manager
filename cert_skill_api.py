from flask import Flask, request, jsonify
import json
from datetime import datetime
import os

app = Flask(__name__)
CERTS_FILE = "certs.json"
LOG_FILE = "renew_log.json"

@app.route("/renew", methods=["POST"])
def renew_cert():
    data = request.get_json()
    host = data.get("host")
    mock = data.get("mock", True)

    if not host:
        return jsonify({"success": False, "output": "host is required"}), 400

    # Update certs.json (mock expiry)
    if os.path.exists(CERTS_FILE):
        with open(CERTS_FILE, "r") as f:
            certs = json.load(f)
    else:
        certs = []

    updated = False
    for cert in certs:
        if cert.get("host") == host:
            cert["mock_expiry"] = (datetime.utcnow().replace(microsecond=0) + 
                                   timedelta(days=90)).strftime("%b %d %H:%M:%S %Y GMT")
            updated = True

    if updated:
        with open(CERTS_FILE, "w") as f:
            json.dump(certs, f, indent=2)

    # Update renew_log.json
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            log = json.load(f)
    else:
        log = {}

    log[host] = datetime.utcnow().isoformat() + "Z"

    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)

    return jsonify({
        "domain": host,
        "success": True,
        "output": f"[MOCK] Simulated renewal for {host}",
        "mode": "MOCK" if mock else "REAL"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
