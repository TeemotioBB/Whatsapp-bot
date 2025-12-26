from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

# ===============================
# Z-API – TOKEN DA INSTÂNCIA (CORRIGIDO)
# ===============================
# Use os dados EXATOS do painel Z-API
ZAPI_INSTANCE = "3EC42CD7178182BE009E5A8D4ACAB450"  # Corrigido
ZAPI_TOKEN = "7F96D7006D280E9EB5081FD1"  # Verifique se este é o token correto

# ===============================
# HEALTH CHECK
# ===============================
@app.route("/", methods=["GET"])
def health():
    return jsonify({
        "status": "online",
        "time": datetime.now().isoformat()
    })

# ===============================
# WEBHOOK
# ===============================
@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    if request.method == "GET":
        return "WEBHOOK OK", 200

    data = request.json
    print("📩 WEBHOOK RECEBIDO:", data)

    if data.get("fromMe"):
        return jsonify({"status": "ignored"})

    phone = data.get("phone")
    message = data.get("text", {}).get("message")

    if not phone or not message:
        return jsonify({"status": "invalid_payload"})

    send_message(phone, f"🤖 Bot ativo!\nVocê disse: {message}")
    return jsonify({"status": "ok"})

# ===============================
# ENVIO DE MENSAGEM
# ===============================
def send_message(phone, text):
    url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}/send-text"
    
    payload = {
        "phone": phone,
        "message": text
    }
    
    headers = {
        "Content-Type": "application/json",
        "Client-Token": ZAPI_TOKEN  # Algumas versões da Z-API exigem este header
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print("📤 RESPOSTA Z-API:", response.status_code, response.text)
        
        if response.status_code == 400:
            print("❌ ERRO: Verifique instanceId e token no painel Z-API")
            
    except Exception as e:
        print("❌ ERRO AO ENVIAR:", e)

# ===============================
# START (RAILWAY)
# ===============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Servidor iniciando na porta {port}")
    print(f"📱 Instance ID: {ZAPI_INSTANCE}")
    print(f"🔑 Token (primeiros 10 chars): {ZAPI_TOKEN[:10]}...")
    app.run(host="0.0.0.0", port=port)
