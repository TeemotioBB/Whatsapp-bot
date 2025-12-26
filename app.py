from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

ZAPI_TOKEN = "7F96D7006D280E9EB5081FD1"

@app.route("/", methods=["GET"])
def health():
    return jsonify({
        "status": "online",
        "time": datetime.now().isoformat()
    })

@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    if request.method == "GET":
        print("✅ Webhook testado com sucesso!")
        return "WEBHOOK OK - Flask está funcionando!", 200

    data = request.json
    print("\n" + "="*50)
    print("📩 WEBHOOK RECEBIDO")
    print(f"Instance ID: {data.get('instanceId')}")
    print(f"De: {data.get('phone')}")
    print(f"Mensagem: {data.get('text', {}).get('message')}")
    print("="*50 + "\n")

    if data.get("fromMe"):
        return jsonify({"status": "ignored"})

    instance_id = data.get("instanceId")
    phone = data.get("phone")
    message = data.get("text", {}).get("message")

    if not instance_id or not phone or not message:
        return jsonify({"status": "invalid_payload"})

    send_message(instance_id, phone, f"🤖 Bot ativo!\nVocê disse: {message}")
    return jsonify({"status": "ok"})

def send_message(instance_id, phone, text):
    url = f"https://api.z-api.io/instances/{instance_id}/token/{ZAPI_TOKEN}/send-text"
    
    payload = {
        "phone": phone,
        "message": text
    }
    
    print(f"📤 Tentando enviar para: {phone}")
    print(f"🔗 URL: {url}")

    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"📤 RESPOSTA Z-API: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ ERRO AO ENVIAR: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"\n🚀 Servidor Flask iniciado!")
    print(f"📍 Porta: {port}")
    print(f"🔗 Webhook: /webhook")
    print(f"🔗 Health check: /")
    print(f"🔑 Token (início): {ZAPI_TOKEN[:10]}...")
    print("-" * 40)
    app.run(host="0.0.0.0", port=port)
