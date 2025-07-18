import subprocess
import platform
from datetime import datetime, timedelta
import json

CERTS_FILE = "certs.json"

def renew_with_certbot(domain, mock_mode=True):
    if mock_mode or platform.system() == "Windows":
        try:
            with open(CERTS_FILE, "r") as f:
                certs = json.load(f)
            updated = False
            for cert in certs:
                if cert["host"] == domain:
                    new_expiry = datetime.utcnow() + timedelta(days=90)
                    cert["mock_expiry"] = new_expiry.strftime("%b %d %H:%M:%S %Y GMT")
                    updated = True
            if updated:
                with open(CERTS_FILE, "w") as f:
                    json.dump(certs, f, indent=2)
                return {
                    "domain": domain,
                    "success": True,
                    "output": f"[MOCK] Simulated renewal for {domain} - expiry updated to {new_expiry}",
                    "mode": "MOCK"
                }
            else:
                return {
                    "domain": domain,
                    "success": False,
                    "output": f"[MOCK] Domain {domain} not found in certs.json",
                    "mode": "MOCK"
                }
        except Exception as e:
            return {
                "domain": domain,
                "success": False,
                "output": f"[MOCK] Error updating certs.json: {str(e)}",
                "mode": "MOCK"
            }

    command = [
        "certbot", "certonly", "--non-interactive",
        "--agree-tos", "--standalone",
        "--register-unsafely-without-email",
        "-d", domain,
        "--deploy-hook", "/bin/bash hooks/reload_nginx.sh"
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        return {
            "domain": domain,
            "success": result.returncode == 0,
            "output": result.stdout if result.returncode == 0 else result.stderr,
            "mode": "REAL"
        }
    except Exception as e:
        return {"domain": domain, "success": False, "output": str(e), "mode": "REAL"}