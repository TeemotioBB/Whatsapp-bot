from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

# ======================
# VARIÁVEIS DE AMBIENTE
# ======================
ZAPI_INSTANCE = os.environ.get("ZAPI_INSTANCE")
ZAPI_TOKEN = os.environ.get("ZAPI_TOKEN")

# ======================
# ROTA PRINCIPAL (opcional)
# ======================
@app.route("/", methods=["GET"])
def health():
    return jsonify({
        "status": "online",
        "time": datetime.now().isoformat()
    })

# ======================
# WEBHOOK Z-API
# ======================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("📩 WEBHOOK RECEBIDO:", data)

    # Segurança: ignora mensagens do próprio bot
    if data.get("fromMe"):
        return jsonify({"status": "ignored"})

    phone = data.get("phone")
    message = (
        data.get("text", {}).get("message")
        or data.get("message")
        or ""
    )

    if not phone or not message:
        return jsonify({"status": "invalid_payload"})

    reply = f"🤖 Bot ativo!\nVocê disse: {message}"
    send_message(phone, reply)

    return jsonify({"status": "ok"})

# ======================
# ENVIO DE MENSAGEM
# ======================
def send_message(phone, text):
    if not ZAPI_INSTANCE or not ZAPI_TOKEN:
        print("❌ ZAPI_INSTANCE ou ZAPI_TOKEN não configurados")
        return

    url = (
        f"https://api.z-api.io/instances/"
        f"{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}/send-text"
    )

    payload = {
        "phone": phone,
        "message": text
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        print("📤 RESPOSTA Z-API:", response.status_code, response.text)
    except Exception as e:
        print("❌ ERRO AO ENVIAR:", str(e))

# ======================
# START SERVER (Railway)
# ======================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Servidor iniciando na porta {port}")
    app.run(host="0.0.0.0", port=port)
