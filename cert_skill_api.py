from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/renew", methods=["POST"])
def renew_cert():
    data = request.get_json()
    host = data.get("host")
    mock = data.get("mock", True)
    
    if not host:
        return jsonify({"success": False, "output": "host is required"}), 400
    
    return jsonify({
        "domain": host,
        "success": True,
        "output": f"[MOCK] Simulated renewal for {host}",
        "mode": "MOCK" if mock else "REAL"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)