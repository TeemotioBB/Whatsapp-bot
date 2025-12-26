from flask import Flask, request
import requests
import os
from datetime import datetime

app = Flask(__name__)

# ================= CONFIGURAÇÃO =================
INSTANCIA = "3EC42CD717B182BE009E5A8D44CAB450"
TOKEN_INSTANCIA = "C1C4D4B66FC02593FCCB149E"
CLIENT_TOKEN = "F0d19adbde8554463ab200473ded89ccbS"
# ================================================

@app.route("/", methods=["GET"])
def index():
    return "🤖 Bot WhatsApp Online"

@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    if request.method == "GET":
        return "✅ Webhook OK", 200
    
    data = request.json
    
    # Ignora mensagens enviadas pelo próprio bot
    if data.get("fromMe"):
        return "Ignorado", 200
    
    phone = data.get("phone")
    message = data.get("text", {}).get("message")
    
    if phone and message:
        # Resposta simples e direta
        resposta = f"✅ Recebi sua mensagem!\n\nVocê disse: {message}\n\nEnviado em: {datetime.now().strftime('%H:%M:%S')}"
        enviar_mensagem(phone, resposta)
    
    return "OK", 200

def enviar_mensagem(phone, text):
    """Envia mensagem via Z-API"""
    url = f"https://api.z-api.io/instances/{INSTANCIA}/token/{TOKEN_INSTANCIA}/send-text"
    
    headers = {
        "Content-Type": "application/json",
        "Client-Token": CLIENT_TOKEN
    }
    
    payload = {"phone": phone, "message": text}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"📤 Resposta Z-API: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Bot iniciado na porta {port}")
    app.run(host="0.0.0.0", port=port)
