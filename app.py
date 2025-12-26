from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

ZAPI_INSTANCE = os.environ.get("ZAPI_INSTANCE")
ZAPI_TOKEN = os.environ.get("ZAPI_TOKEN")

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    # Ignora mensagens enviadas pelo próprio bot
    if data.get("fromMe"):
        return jsonify({"status": "ok"})

    phone = data["phone"]
    message = data.get("text", {}).get("message", "")

    if not message:
        return jsonify({"status": "ok"})

    reply = f"🤖 Bot ativo!\nVocê disse: {message}"

    send_message(phone, reply)
    return jsonify({"status": "ok"})

def send_message(phone, text):
    url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}/send-text"
    payload = {
        "phone": phone,
        "message": text
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
