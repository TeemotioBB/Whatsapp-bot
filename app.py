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

# Simula um "banco de dados" de usuários que já foram atendidos
usuarios_atendidos = {}

def criar_resposta(nome, mensagem, primeira_vez=False):
    """Cria respostas personalizadas"""
    
    if primeira_vez:
        return f"""👋 *Olá {nome}! Seja bem-vindo(a)!*

🤖 *Eu sou o Assistente Virtual*
Estou aqui para te ajudar com:
• Informações
• Suporte
• Dúvidas

*Como posso ajudá-lo(a) hoje?*

_Digite 'ajuda' para ver os comandos disponíveis._"""
    
    mensagem = mensagem.lower()
    
    # Comandos/respostas
    respostas = {
        "oi": f"Olá {nome}! 😊\nComo posso te ajudar hoje?",
        "ola": f"Olá {nome}! 😊\nEm que posso ser útil?",
        "tudo bem": "Tudo ótimo! E com você? 😄",
        "bom dia": f"Bom dia, {nome}! ☀️\nQue seu dia seja excelente!",
        "boa tarde": f"Boa tarde, {nome}! 🌤️",
        "boa noite": f"Boa noite, {nome}! 🌙\nDurma bem!",
        "ajuda": """🤖 *COMANDOS DISPONÍVEIS*

• *oi/olá* - Saudação
• *horas* - Ver hora atual
• *data* - Ver data atual
• *criador* - Quem me criou
• *ajuda* - Mostra esta mensagem

_Pergunte qualquer coisa!_""",
        "horas": f"🕒 São *{datetime.now().strftime('%H:%M:%S')}*",
        "data": f"📅 Hoje é *{datetime.now().strftime('%d/%m/%Y')}*",
        "criador": "👨‍💻 *Criador:* Maycon Johnny\n\nEste bot foi desenvolvido para atendimento automático no WhatsApp!",
        "obrigado": "De nada! 😊\nEstou aqui para ajudar!",
        "valeu": "Por nada! 👍\nPrecisa de mais alguma coisa?",
        "tchau": "Até logo! 👋\nVolte sempre!",
        "adeus": "Até mais! 😊\nTenha um ótimo dia!"
    }
    
    # Procura resposta exata
    if mensagem in respostas:
        return respostas[mensagem]
    
    # Se não encontrar resposta específica
    return f"""🤖 *Entendido, {nome}!*

Você disse: *"{mensagem.capitalize()}"*

Não tenho uma resposta específica para isso ainda, mas estou aprendendo!

Digite *'ajuda'* para ver o que posso fazer por você! 😊"""

@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    if request.method == "GET":
        return "✅ Webhook Ativo", 200
    
    data = request.json
    
    # Ignora mensagens enviadas pelo próprio bot
    if data.get("fromMe"):
        return "OK", 200
    
    phone = data.get("phone")
    nome = data.get("senderName", "Usuário")
    mensagem = data.get("text", {}).get("message", "").strip()
    
    if not phone or not mensagem:
        return "OK", 200
    
    # Verifica se é a primeira mensagem deste usuário
    primeira_vez = phone not in usuarios_atendidos
    if primeira_vez:
        usuarios_atendidos[phone] = {
            "nome": nome,
            "primeira_interacao": datetime.now().isoformat()
        }
    
    # Cria resposta personalizada
    resposta = criar_resposta(nome, mensagem, primeira_vez)
    
    # Envia a resposta
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
        print(f"✅ Mensagem enviada para {phone}")
    except Exception as e:
        print(f"❌ Erro: {e}")

@app.route("/teste", methods=["GET"])
def teste():
    """Rota para teste manual"""
    phone = request.args.get("phone", "553191316890")
    nome = request.args.get("nome", "Teste")
    msg = request.args.get("msg", "Oi")
    
    # Simula primeira interação
    primeira_vez = True
    resposta = criar_resposta(nome, msg, primeira_vez)
    
    enviar_mensagem(phone, resposta)
    
    return f"Teste enviado para {phone}"

@app.route("/", methods=["GET"])
def status():
    return f"""
    <html>
        <head><title>🤖 Bot WhatsApp</title></head>
        <body style="font-family: Arial; padding: 20px;">
            <h1>🤖 Bot WhatsApp Online</h1>
            <p><strong>Status:</strong> ✅ Operacional</p>
            <p><strong>Usuários atendidos:</strong> {len(usuarios_atendidos)}</p>
            <p><strong>Endpoints:</strong></p>
            <ul>
                <li><code>/webhook</code> - Webhook principal</li>
                <li><code>/teste</code> - Teste manual</li>
            </ul>
        </body>
    </html>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"🤖 Bot iniciado na porta {port}")
    print(f"📱 Instance: {INSTANCIA}")
    print("🔗 Webhook: /webhook")
    app.run(host="0.0.0.0", port=port)
