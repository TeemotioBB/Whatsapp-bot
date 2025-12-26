from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime
import time

app = Flask(__name__)

# ===============================
# ✅ NOVOS DADOS ATUALIZADOS
# ===============================
ZAPI_INSTANCE = "3EC42CD717B182BE009E5A8D44CAB450"
ZAPI_TOKEN = "C1C4D4B66FC02593FCCB149E"  # NOVO TOKEN!

# ===============================
# WEBHOOK PRINCIPAL
# ===============================
@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    if request.method == "GET":
        return jsonify({
            "status": "ready",
            "instance": ZAPI_INSTANCE,
            "token": ZAPI_TOKEN[:8] + "...",
            "time": datetime.now().isoformat()
        }), 200

    data = request.json
    print(f"\n{'='*60}")
    print(f"📩 MENSAGEM RECEBIDA - {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}")
    print(f"👤 De: {data.get('senderName')} ({data.get('phone')})")
    print(f"💬 Texto: '{data.get('text', {}).get('message', '')}'")
    print(f"🆔 Instance ID: {data.get('instanceId')}")
    print(f"✅ Token usado: {ZAPI_TOKEN}")
    print(f"{'='*60}")

    if data.get("fromMe"):
        return jsonify({"status": "ignored"})

    phone = data.get("phone")
    message = data.get("text", {}).get("message")

    if not phone or not message:
        return jsonify({"status": "invalid_payload"})

    # Resposta automática
    resposta = f"""✅ *Mensagem Recebida com Sucesso!*

*Seu texto:* {message}

*Detalhes:*
📅 Data: {datetime.now().strftime('%d/%m/%Y')}
⏰ Hora: {datetime.now().strftime('%H:%M:%S')}
🤖 Bot: Online e funcionando!

_Esta é uma resposta automática do seu bot._"""

    # Tenta enviar a resposta
    success = send_message_zapi(phone, resposta)
    
    if success:
        print("🎉 RESPOSTA ENVIADA COM SUCESSO!")
        return jsonify({"status": "success", "message": "sent"})
    else:
        print("⚠️ Falha ao enviar resposta")
        return jsonify({"status": "error", "message": "send_failed"}), 500

# ===============================
# FUNÇÃO DE ENVIO OTIMIZADA
# ===============================
def send_message_zapi(phone, text):
    """Envia mensagem via Z-API com novo token"""
    
    url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}/send-text"
    
    payload = {
        "phone": phone,
        "message": text
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    print(f"\n📤 TENTANDO ENVIAR RESPOSTA...")
    print(f"🔗 URL: {url}")
    print(f"📱 Para: {phone}")
    print(f"📝 Mensagem: {text[:50]}...")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        
        print(f"\n📊 RESPOSTA DA Z-API:")
        print(f"Status: {response.status_code}")
        print(f"Conteúdo: {response.text}")
        
        if response.status_code == 200:
            print("✅ ✅ ✅ ENVIO BEM-SUCEDIDO!")
            print(f"Token {ZAPI_TOKEN} está FUNCIONANDO!")
            return True
            
        elif response.status_code == 400:
            error_data = response.json()
            error_msg = error_data.get("error", "Erro desconhecido")
            print(f"❌ ERRO 400: {error_msg}")
            
            # Análise específica do erro
            if "client-token" in error_msg.lower():
                print("\n🔍 DIAGNÓSTICO DO ERRO 'client-token not configured':")
                print("1. O token foi gerado há menos de 2 minutos?")
                print("2. A instância foi reiniciada após gerar novo token?")
                print("3. O WhatsApp está conectado na instância?")
                
                # Sugere teste manual
                print("\n💡 TESTE MANUAL (execute no terminal):")
                print(f'curl -X POST "{url}" \\')
                print('  -H "Content-Type: application/json" \\')
                print(f'  -d \'{{"phone": "{phone}", "message": "Teste direto"}}\'')
                
        elif response.status_code == 404:
            print("❌ ERRO 404: Instância não encontrada")
            print("   Verifique se a instância ainda está ativa no painel")
            
        else:
            print(f"⚠️ Status inesperado: {response.status_code}")
            
        return False
        
    except Exception as e:
        print(f"❌ EXCEÇÃO: {str(e)}")
        return False

# ===============================
# ROTA DE TESTE MANUAL
# ===============================
@app.route("/teste-envio", methods=["GET"])
def teste_envio():
    """Rota para testar envio manualmente"""
    phone = request.args.get("phone", "553191316890")
    message = request.args.get("msg", "Teste do bot com novo token")
    
    print(f"\n🧪 TESTE MANUAL SOLICITADO")
    print(f"Para: {phone}")
    print(f"Mensagem: {message}")
    print(f"Token usado: {ZAPI_TOKEN}")
    
    success = send_message_zapi(phone, f"🧪 Teste Manual:\n{message}\n\nToken: {ZAPI_TOKEN[:8]}...")
    
    if success:
        return jsonify({
            "status": "test_success",
            "to": phone,
            "token": ZAPI_TOKEN[:8] + "...",
            "timestamp": datetime.now().isoformat()
        })
    else:
        return jsonify({
            "status": "test_failed",
            "error": "Falha no envio",
            "token": ZAPI_TOKEN[:8] + "..."
        }), 500

# ===============================
# VERIFICAÇÃO DE CONEXÃO
# ===============================
@app.route("/status", methods=["GET"])
def status():
    """Verifica status da instância e token"""
    url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}/instance"
    
    try:
        response = requests.get(url, timeout=10)
        return jsonify({
            "instance": ZAPI_INSTANCE,
            "token": ZAPI_TOKEN[:8] + "...",
            "api_status": response.status_code,
            "response": response.json() if response.status_code == 200 else response.text,
            "webhook_url": "https://whatsapp-bot-production-1ad3.up.railway.app/webhook",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===============================
# INICIALIZAÇÃO
# ===============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    
    print(f"\n{'='*70}")
    print("🤖 WHATSAPP BOT - NOVA CONFIGURAÇÃO")
    print("="*70)
    print(f"📱 Instance ID: {ZAPI_INSTANCE}")
    print(f"🔑 NOVO TOKEN: {ZAPI_TOKEN}")
    print(f"🔗 URL Completa:")
    print(f"   https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}/send-text")
    print(f"🌐 Seu Webhook:")
    print(f"   https://whatsapp-bot-production-1ad3.up.railway.app/webhook")
    print("="*70)
    print("📋 ROTAS PARA TESTE:")
    print(f"   • GET /             - Health check")
    print(f"   • GET /webhook      - Teste webhook")
    print(f"   • GET /status       - Status da instância")
    print(f"   • GET /teste-envio  - Teste manual")
    print(f"   • GET /teste-envio?phone=553191316890&msg=Olá")
    print("="*70)
    print("\n⚠️  CONFIGURAÇÃO NECESSÁRIA:")
    print("1. No Z-API, vá em 'Webhooks e configurações gerais'")
    print("2. Configure a URL: https://whatsapp-bot-production-1ad3.up.railway.app/webhook")
    print("3. Marque 'Ao receber mensagem'")
    print("4. SALVE as configurações")
    print("5. REINICIE a instância (opcional)")
    print("="*70)
    
    app.run(host="0.0.0.0", port=port, debug=False)
