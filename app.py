from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

# ===============================
# TOKENS PARA CADA INSTÂNCIA
# ===============================
INSTANCE_TOKENS = {
    # Instância A (do painel)
    "3EC42CD7178182BE009E5A8D4ACAB450": "7F96D7006D280E9EB5081FD1",
    
    # Instância B (que envia webhooks) - VOCÊ PRECISA PEGAR O TOKEN CERTO!
    "3EC42CD717B182BE009E5A8D44CAB450": "TOKEN_DA_INSTANCIA_B_AQUI"
}

@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "online", "time": datetime.now().isoformat()})

@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    if request.method == "GET":
        return "WEBHOOK OK", 200

    data = request.json
    print("\n" + "="*50)
    print("📩 WEBHOOK RECEBIDO")
    instance_id = data.get("instanceId")
    print(f"Instance ID: {instance_id}")
    print(f"De: {data.get('phone')}")
    print(f"Mensagem: {data.get('text', {}).get('message')}")
    print("="*50 + "\n")

    if data.get("fromMe"):
        return jsonify({"status": "ignored"})

    phone = data.get("phone")
    message = data.get("text", {}).get("message")

    if not instance_id or not phone or not message:
        return jsonify({"status": "invalid_payload"})

    # Verifica se temos token para esta instância
    token = INSTANCE_TOKENS.get(instance_id)
    
    if not token:
        print(f"❌ NÃO ENCONTRADO token para a instância: {instance_id}")
        print("   Adicione o token desta instância no dicionário INSTANCE_TOKENS")
        return jsonify({"status": "instance_not_configured"})

    send_message(instance_id, token, phone, f"🤖 Bot ativo!\nVocê disse: {message}")
    return jsonify({"status": "ok"})

def send_message(instance_id, token, phone, text):
    url = f"https://api.z-api.io/instances/{instance_id}/token/{token}/send-text"
    
    payload = {
        "phone": phone,
        "message": text
    }
    
    print(f"📤 Enviando para: {phone}")
    print(f"🔗 Usando token: {token[:10]}...")

    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"📤 RESPOSTA Z-API: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ ERRO AO ENVIAR: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"\n🚀 Servidor Flask iniciado!")
    print(f"🔑 Instâncias configuradas: {len(INSTANCE_TOKENS)}")
    app.run(host="0.0.0.0", port=port)
