from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

# ==================================================
# CONFIGURAÇÕES Z-API (CLIENT TOKEN ATIVO)
# ==================================================
ZAPI_INSTANCE = "3EC42CD717B182BE009E5A8D44CAB450"
CLIENT_TOKEN = "F0d19adbde8554463ab200473ded89ccbS"

# ==================================================
# HEALTH CHECK
# ==================================================
@app.route("/", methods=["GET"])
def health():
    return jsonify({
        "status": "online",
        "time": datetime.now().isoformat()
    })

# ==================================================
# WEBHOOK Z-API
# ==================================================
@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    if request.method == "GET":
        return "WEBHOOK OK", 200

    data = request.json
    print("📩 WEBHOOK RECEBIDO:", data)

    # Ignora mensagens enviadas pelo próprio número
    if data.get("fromMe"):
        return jsonify({"status": "ignored"})

    phone = data.get("phone")
    message = data.get("text", {}).get("message")

    if not phone or not message:
        print("⚠️ Payload inválido")
        return jsonify({"status": "invalid_payload"})

    reply = f"🤖 Bot ativo!\nVocê disse: {message}"
    send_message(phone, reply)

    return jsonify({"status": "ok"})

# ==================================================
# ENVIO DE MENSAGEM (ENDPOINT CORRETO + CLIENT TOKEN)
# ==================================================
def send_message(phone, text):
    url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/messages/send-text"

    payload = {
        "phone": phone,
        "message": text
    }

    headers = {
        "client-token": CLIENT_TOKEN,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=10
        )
        print("📤 RESPOSTA Z-API:", response.status_code, response.text)
    except Exception as e:
        print("❌ ERRO AO ENVIAR:", e)

# ==================================================
# START SERVER (RAILWAY)
# ==================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Servidor iniciando na porta {port}")
    app.run(host="0.0.0.0", port=port)
