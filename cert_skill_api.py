from flask import Flask, request, jsonify
from cert_renewer import renew_with_certbot

app = Flask(__name__)

@app.route("/renew", methods=["POST"])
def renew():
    data = request.get_json()
    domain = data.get("host")
    mock = data.get("mock", True)
    if not domain:
        return jsonify({"success": False, "output": "host is required"}), 400
    result = renew_with_certbot(domain, mock_mode=mock)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
