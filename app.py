from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

# ===============================
# ✅ SEUS DADOS CORRETOS (CONFIRMADOS)
# ===============================
ZAPI_INSTANCE = "3EC42CD717B182BE009E5A8D44CAB450"
ZAPI_TOKEN = "C1C4D4B66FC02593FCCB149E"  # Token da instância
ZAPI_CLIENT_TOKEN = "F0d19adbde8554463ab200473ded89ccbS"  # Client Token

# ===============================
# HEALTH CHECK
# ===============================
@app.route("/", methods=["GET"])
def health():
    return jsonify({
        "status": "online",
        "instance": ZAPI_INSTANCE,
        "time": datetime.now().isoformat()
    }), 200

# ===============================
# WEBHOOK PRINCIPAL
# ===============================
@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    if request.method == "GET":
        print("✅ Webhook testado via GET")
        return jsonify({
            "status": "ready",
            "webhook": "active",
            "instance": ZAPI_INSTANCE,
            "timestamp": datetime.now().isoformat()
        }), 200

    # Processa mensagem recebida
    data = request.json
    print(f"\n{'='*60}")
    print(f"📩 MENSAGEM RECEBIDA - {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}")
    print(f"👤 De: {data.get('senderName')} ({data.get('phone')})")
    print(f"💬 Texto: '{data.get('text', {}).get('message', '')}'")
    print(f"{'='*60}")

    # Ignora mensagens enviadas pelo próprio bot
    if data.get("fromMe"):
        print("⏭️ Ignorando mensagem enviada por mim")
        return jsonify({"status": "ignored"}), 200

    # Extrai dados da mensagem
    phone = data.get("phone")
    message = data.get("text", {}).get("message")

    if not phone or not message:
        print("❌ Dados incompletos")
        return jsonify({"status": "invalid_payload"}), 400

    # Prepara resposta
    resposta = f"""✅ *Mensagem Recebida com Sucesso!*

*Você disse:* {message}

📅 *Data:* {datetime.now().strftime('%d/%m/%Y')}
⏰ *Hora:* {datetime.now().strftime('%H:%M:%S')}
🤖 *Status:* Bot online e funcionando!

_Esta é uma resposta automática do seu bot._"""

    # Envia resposta
    success, response_data = send_message(phone, resposta)
    
    if success:
        print("🎉 Resposta enviada com sucesso!")
        return jsonify({"status": "message_sent", "data": response_data}), 200
    else:
        print("⚠️ Falha ao enviar resposta")
        return jsonify({"status": "send_failed", "error": response_data}), 500

# ===============================
# FUNÇÃO DE ENVIO CORRIGIDA
# ===============================
def send_message(phone, text):
    """Envia mensagem via Z-API com todos os tokens corretos"""
    
    # URL CORRETA da Z-API v1
    url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}/send-text"
    
    payload = {
        "phone": phone,
        "message": text
    }
    
    # HEADERS OBRIGATÓRIOS
    headers = {
        "Content-Type": "application/json",
        "Client-Token": ZAPI_CLIENT_TOKEN,  # ⚠️ IMPORTANTE!
        "Accept": "application/json"
    }
    
    print(f"\n📤 ENVIANDO MENSAGEM...")
    print(f"🔗 URL: {url}")
    print(f"📱 Para: {phone}")
    print(f"🔑 Instance Token: {ZAPI_TOKEN}")
    print(f"👤 Client Token: {ZAPI_CLIENT_TOKEN[:10]}...")
    print(f"📝 Mensagem: {text[:80]}...")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        
        print(f"\n📊 RESPOSTA DA Z-API:")
        print(f"Status Code: {response.status_code}")
        print(f"Resposta: {response.text}")
        
        if response.status_code == 200:
            print("✅ ✅ ✅ MENSAGEM ENVIADA COM SUCESSO!")
            return True, response.json()
            
        elif response.status_code == 201:
            print("✅ ✅ ✅ MENSAGEM ENVIADA (Status 201)!")
            return True, response.json()
            
        elif response.status_code == 400:
            error_data = response.json()
            error_msg = error_data.get("error", "")
            print(f"❌ ERRO 400: {error_msg}")
            
            # Sugere soluções específicas
            if "client-token" in error_msg.lower():
                print("\n🔍 PROBLEMA NO CLIENT-TOKEN:")
                print("1. Verifique se o Client Token está correto")
                print(f"2. Seu Client Token: {ZAPI_CLIENT_TOKEN}")
                print("3. Verifique no painel Z-API se está ativo")
                
            return False, error_data
            
        elif response.status_code == 401:
            print("❌ ERRO 401: Não autorizado")
            print("   Verifique Client Token e Instance Token")
            return False, {"error": "Unauthorized"}
            
        elif response.status_code == 404:
            print("❌ ERRO 404: Recurso não encontrado")
            print("   Verifique se a URL está correta")
            print(f"   URL usada: {url}")
            return False, {"error": "Not Found"}
            
        else:
            print(f"⚠️ Status inesperado: {response.status_code}")
            return False, {"error": f"Status {response.status_code}", "response": response.text}
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT: A requisição demorou muito (15s)")
        return False, {"error": "Timeout"}
        
    except requests.exceptions.ConnectionError:
        print("❌ ERRO DE CONEXÃO: Não foi possível conectar à Z-API")
        return False, {"error": "Connection Error"}
        
    except Exception as e:
        print(f"❌ ERRO INESPERADO: {str(e)}")
        return False, {"error": str(e)}

# ===============================
# ROTA PARA TESTE MANUAL
# ===============================
@app.route("/test", methods=["GET"])
def test_send():
    """Rota para teste manual do envio"""
    
    phone = request.args.get("phone", "553191316890")
    message = request.args.get("message", "Teste do bot WhatsApp")
    
    print(f"\n🧪 TESTE MANUAL SOLICITADO")
    print(f"Para: {phone}")
    
    test_message = f"""🧪 *TESTE MANUAL DO BOT*

{message}

📱 *Instance ID:* {ZAPI_INSTANCE}
🔑 *Token:* {ZAPI_TOKEN[:8]}...
👤 *Client Token:* {ZAPI_CLIENT_TOKEN[:8]}...
🕒 *Hora:* {datetime.now().strftime('%H:%M:%S')}

_Teste realizado com sucesso!_"""
    
    success, response_data = send_message(phone, test_message)
    
    if success:
        return jsonify({
            "status": "success",
            "message": "Mensagem enviada",
            "to": phone,
            "response": response_data,
            "timestamp": datetime.now().isoformat()
        }), 200
    else:
        return jsonify({
            "status": "error",
            "message": "Falha ao enviar",
            "to": phone,
            "error": response_data,
            "timestamp": datetime.now().isoformat()
        }), 500

# ===============================
# ROTA PARA VERIFICAR TOKENS
# ===============================
@app.route("/tokens", methods=["GET"])
def show_tokens():
    """Mostra os tokens configurados (sem expor completamente)"""
    return jsonify({
        "instance_id": ZAPI_INSTANCE,
        "instance_token_prefix": ZAPI_TOKEN[:8] + "...",
        "client_token_prefix": ZAPI_CLIENT_TOKEN[:8] + "...",
        "tokens_length": {
            "instance_token": len(ZAPI_TOKEN),
            "client_token": len(ZAPI_CLIENT_TOKEN)
        },
        "status": "configured",
        "timestamp": datetime.now().isoformat()
    })

# ===============================
# VERIFICAÇÃO DA INSTÂNCIA
# ===============================
@app.route("/check", methods=["GET"])
def check_instance():
    """Verifica o status da instância"""
    
    url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}/instance"
    
    headers = {
        "Client-Token": ZAPI_CLIENT_TOKEN,
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        return jsonify({
            "instance": ZAPI_INSTANCE,
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else response.text,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "instance": ZAPI_INSTANCE,
            "timestamp": datetime.now().isoformat()
        }), 500

# ===============================
# INICIALIZAÇÃO DO SERVIDOR
# ===============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    
    print(f"\n{'='*70}")
    print("🤖 WHATSAPP BOT - CONFIGURADO COM SUCESSO!")
    print("="*70)
    print(f"📍 Porta: {port}")
    print(f"📱 Instance ID: {ZAPI_INSTANCE}")
    print(f"🔑 Instance Token: {ZAPI_TOKEN}")
    print(f"👤 Client Token: {ZAPI_CLIENT_TOKEN[:10]}...")
    print("="*70)
    print("🌐 URLs importantes:")
    print(f"   • Webhook: https://whatsapp-bot-production-1ad3.up.railway.app/webhook")
    print(f"   • Health: https://whatsapp-bot-production-1ad3.up.railway.app/")
    print(f"   • Teste: https://whatsapp-bot-production-1ad3.up.railway.app/test")
    print(f"   • Status: https://whatsapp-bot-production-1ad3.up.railway.app/check")
    print("="*70)
    print("📋 Como testar:")
    print("1. Envie 'oi' para o número conectado no WhatsApp")
    print("2. Ou acesse: /test?phone=553191316890&message=Testando")
    print("3. Verifique os logs abaixo")
    print("="*70 + "\n")
    
    app.run(host="0.0.0.0", port=port, debug=False)
