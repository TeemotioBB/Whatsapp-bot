from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

# ===============================
# ✅ SEUS DADOS CORRETOS (CONFIRMADOS)
# ===============================
ZAPI_INSTANCE = "3EC42CD717B182BE009E5A8D44CAB450"
ZAPI_TOKEN = "7F96D7006D280E9EB5081FD1"

# ===============================
# HEALTH CHECK
# ===============================
@app.route("/", methods=["GET"])
def health():
    return jsonify({
        "status": "online",
        "instance": ZAPI_INSTANCE[:10] + "...",
        "time": datetime.now().isoformat()
    })

# ===============================
# WEBHOOK PRINCIPAL
# ===============================
@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    if request.method == "GET":
        print("✅ Webhook testado - Tudo OK!")
        return jsonify({
            "status": "ready",
            "instance": ZAPI_INSTANCE,
            "webhook": "configured"
        }), 200

    data = request.json
    print("\n" + "="*60)
    print("📩 MENSAGEM RECEBIDA VIA WEBHOOK")
    print(f"ID da Instância: {data.get('instanceId')}")
    print(f"Esperado: {ZAPI_INSTANCE}")
    print(f"De: {data.get('phone')} ({data.get('senderName')})")
    print(f"Texto: '{data.get('text', {}).get('message')}'")
    print("="*60)

    # Verifica se a instância bate com a configurada
    if data.get("instanceId") != ZAPI_INSTANCE:
        print(f"⚠️  Atenção: Instância diferente!")
        print(f"   Recebido: {data.get('instanceId')}")
        print(f"   Configurado: {ZAPI_INSTANCE}")

    if data.get("fromMe"):
        print("📤 Ignorando mensagem enviada por mim")
        return jsonify({"status": "ignored"})

    phone = data.get("phone")
    message = data.get("text", {}).get("message")

    if not phone or not message:
        return jsonify({"status": "invalid_payload"})

    # Resposta personalizada
    resposta = f"""🤖 *BOT ATIVO!*

✅ *Mensagem recebida:* {message}

📱 *De:* {data.get('senderName', 'Usuário')}
🕒 *Hora:* {datetime.now().strftime('%H:%M:%S')}

_Esta é uma resposta automática do bot._"""

    # Envia resposta
    success = send_message(phone, resposta)
    
    if success:
        return jsonify({"status": "message_sent"})
    else:
        return jsonify({"status": "send_failed"}), 500

# ===============================
# FUNÇÃO DE ENVIO COM TRATAMENTO DE ERROS
# ===============================
def send_message(phone, text):
    url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}/send-text"
    
    payload = {
        "phone": phone,
        "message": text
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"\n📤 ENVIANDO RESPOSTA PARA {phone}...")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Resposta Bruta: {response.text}")
        
        if response.status_code == 200:
            print("✅ ✅ ✅ MENSAGEM ENVIADA COM SUCESSO!")
            return True
            
        elif response.status_code == 400:
            error_data = response.json()
            if "error" in error_data:
                error_msg = error_data["error"]
                print(f"❌ ERRO 400: {error_msg}")
                
                if "client-token" in error_msg.lower():
                    print("⚠️  Problema com o token. Verifique:")
                    print(f"   1. Token correto: {ZAPI_TOKEN}")
                    print(f"   2. Instância correta: {ZAPI_INSTANCE}")
                    print(f"   3. Token configurado no painel Z-API")
                    
        elif response.status_code == 404:
            print("❌ ERRO 404: Instância não encontrada")
            print(f"   URL usada: {url}")
            print("   Verifique se a instância ainda está ativa no painel Z-API")
            
        elif response.status_code == 401:
            print("❌ ERRO 401: Token inválido ou expirado")
            print("   Gere um novo token no painel Z-API")
            
        else:
            print(f"❌ ERRO DESCONHECIDO: {response.status_code}")
            print(f"   Resposta: {response.text}")
            
        return False
        
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT: A requisição demorou muito")
        return False
        
    except requests.exceptions.ConnectionError:
        print("❌ ERRO DE CONEXÃO: Não foi possível conectar à Z-API")
        return False
        
    except Exception as e:
        print(f"❌ ERRO INESPERADO: {str(e)}")
        return False

# ===============================
# TESTE MANUAL (opcional)
# ===============================
@app.route("/test", methods=["GET"])
def test_send():
    """Rota para teste manual do envio"""
    phone = request.args.get("phone", "553191316890")
    message = request.args.get("message", "Teste do bot")
    
    success = send_message(phone, f"🧪 Teste manual:\n{message}")
    
    if success:
        return jsonify({"status": "test_sent", "to": phone})
    else:
        return jsonify({"status": "test_failed"}), 500

# ===============================
# VERIFICAÇÃO DA INSTÂNCIA
# ===============================
@app.route("/check-instance", methods=["GET"])
def check_instance():
    """Verifica se a instância está ativa"""
    url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}/instance"
    
    try:
        response = requests.get(url, timeout=10)
        return jsonify({
            "status": "instance_check",
            "code": response.status_code,
            "response": response.json() if response.status_code == 200 else response.text
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===============================
# INICIALIZAÇÃO
# ===============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    
    print("\n" + "="*70)
    print("🤖 WHATSAPP BOT - CONFIGURAÇÃO ATUAL")
    print("="*70)
    print(f"📍 Porta do servidor: {port}")
    print(f"📱 Instance ID: {ZAPI_INSTANCE}")
    print(f"🔑 Token: {ZAPI_TOKEN}")
    print(f"🔗 URL da API: https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}/send-text")
    print(f"🌐 Seu webhook: https://whatsapp-bot-production-1ad3.up.railway.app/webhook")
    print("="*70)
    print("📋 ROTAS DISPONÍVEIS:")
    print(f"   GET  /               - Health check")
    print(f"   GET  /webhook        - Teste webhook")
    print(f"   POST /webhook        - Recebe mensagens")
    print(f"   GET  /test           - Teste envio manual")
    print(f"   GET  /check-instance - Verifica instância")
    print("="*70)
    print("\n⚠️  CONFIGURAÇÃO NO Z-API:")
    print("1. Acesse: https://console.z-api.io")
    print("2. Vá na sua instância")
    print("3. Em 'Webhooks', configure:")
    print(f"   URL: https://whatsapp-bot-production-1ad3.up.railway.app/webhook")
    print("4. Salve e teste enviando uma mensagem!")
    print("="*70 + "\n")
    
    app.run(host="0.0.0.0", port=port, debug=False)
