from flask import Flask, request
import requests
import os
from datetime import datetime

app = Flask(__name__)

# ================== CONFIGURAÇÕES ==================
ZAPI_INSTANCE = "3EC42CD717B182BE009E5A8D44CAB450"  # ✅ Corrigido
TOKEN_INSTANCIA = "C1C4D4B66FC02593FCCB149E"
CLIENT_TOKEN = "F0d19adbde8554463ab200473ded89ccbS"
OPENAI_API_KEY = "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"
# ===================================================

# ================== MEMÓRIA TEMPORÁRIA ==================
user_memory = {}
# =======================================================

@app.route("/", methods=["GET"])
def index():
    return "🤖 Bot Fitness Online ✅"

@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    if request.method == "GET":
        return "✅ Webhook OK", 200

    data = request.json
    print(f"\n📩 WEBHOOK RECEBIDO: {data.get('text', {}).get('message', '')[:50]}...")

    if data.get("fromMe"):
        return "ignored", 200

    phone = data.get("phone")
    text = data.get("text", {}).get("message")
    image = data.get("image", {}).get("imageUrl")

    if image:
        resposta = analisar_imagem(image)
        enviar_mensagem(phone, resposta)
        return "ok", 200

    if text:
        resposta = tratar_texto(phone, text)
        enviar_mensagem(phone, resposta)

    return "ok", 200

# ================== TEXTO ==================
def tratar_texto(phone, text):
    text_lower = text.lower().strip()
    
    # Primeira mensagem?
    if phone not in user_memory:
        user_memory[phone] = {
            "nome": text if len(text.split()) == 1 else "Amigo",
            "treinos": [],
            "refeicoes": [],
            "primeira_interacao": datetime.now().isoformat()
        }
        return f"""👋 Olá! Eu sou seu *Personal Trainer Virtual*! 🤖

Estou aqui para ajudar você com:
🏋️‍♂️ *Registro de treinos*
🥗 *Análise de alimentação*
📊 *Relatórios de progresso*
💪 *Motivação diária*

*Comandos disponíveis:*
• *"treinei"* - Registrar treino
• *"relatório"* - Ver seu progresso
• Envie foto de comida para análise
• Envie foto do shape para feedback

Vamos juntos nessa jornada! 💪"""

    # Comandos
    if "treinei" in text_lower:
        registrar_treino(phone)
        return "✅ *Treino registrado com sucesso!* 🏋️‍♂️\n\nContinue assim! 💪"

    if "relatório" in text_lower:
        return gerar_relatorio(phone)
    
    if text_lower in ["oi", "ola", "olá"]:
        return f"Olá! 😊\nComo posso te ajudar hoje?"
    
    if text_lower == "ajuda":
        return """🤖 *COMANDOS DO PERSONAL TRAINER*

🏋️ *"treinei"* - Registrar treino do dia
📊 *"relatório"* - Ver progresso
🥗 *Envie foto* de comida para análise
💪 *Envie foto* do shape para feedback
📅 *"dicas"* - Dicas de treino/alimentação

*Estou aqui para te ajudar a alcançar seus objetivos!* 💪"""
    
    if text_lower == "dicas":
        return """💡 *DICAS RÁPIDAS*

🏋️‍♂️ *Treino:*
• Consistência > Intensidade
• Descanse 48h entre treinos do mesmo grupo
• Hidrate-se durante o treino

🥗 *Alimentação:*
• Proteína em todas as refeições
• Hidrate-se bem (2-3L água/dia)
• Prefira alimentos naturais

💤 *Descanso:*
• Durma 7-8h por noite
• O músculo cresce no descanso!"""

    # Se não for comando, usa ChatGPT
    return responder_chatgpt(f"Usuário diz: {text}\n\nResponda como um personal trainer motivador, dando dicas úteis sobre fitness, nutrição e saúde. Seja positivo e encorajador.")

# ================== TREINO ==================
def registrar_treino(phone):
    user_memory.setdefault(phone, {"treinos": [], "refeicoes": []})
    user_memory[phone]["treinos"].append({
        "data": datetime.now().date().isoformat(),
        "hora": datetime.now().strftime("%H:%M:%S")
    })

# ================== RELATÓRIO ==================
def gerar_relatorio(phone):
    dados = user_memory.get(phone)

    if not dados or len(dados.get("treinos", [])) == 0:
        return "📊 *RELATÓRIO*\n\nAinda não tenho dados suficientes.\n\nRegistre seu primeiro treino com *'treinei'*! 💪"

    treinos = len(dados["treinos"])
    refeicoes = len(dados.get("refeicoes", []))
    
    return f"""📊 *SEU RELATÓRIO DE PROGRESSO*

✅ *Treinos registrados:* {treinos}
🥗 *Refeições analisadas:* {refeicoes}
📅 *Desde:* {dados.get('primeira_interacao', 'Hoje')[:10]}

🎯 *Estatísticas:*
• Média: {treinos/7:.1f} treinos/semana
• Nível: {'🔥 Avançado' if treinos > 10 else '🚀 Intermediário' if treinos > 5 else '⭐ Iniciante'}

💪 *Continue assim!* Cada treino te aproxima do seu objetivo!"""

# ================== IMAGEM ==================
def analisar_imagem(image_url):
    return responder_chatgpt(
        """Analise a imagem como um personal trainer e nutricionista:
        
        1. Se for COMIDA:
           - Calorias estimadas
           - Macronutrientes (proteínas, carbs, gorduras)
           - Dica nutricional rápida
           - Sugestão de ajuste se necessário
        
        2. Se for SHAPE/Corpo:
           - Pontos fortes visíveis
           - Áreas para melhorar
           - Dica de treino específica
           - Motivação
        
        3. Se for outra coisa:
           - Relacione com fitness se possível
           - Dê uma dica motivacional
        
        Seja positivo, construtivo e profissional!""",
        image_url
    )

# ================== CHATGPT ==================
def responder_chatgpt(prompt, image_url=None):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    if image_url:
        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]
        }]
    else:
        messages = [{"role": "user", "content": prompt}]

    payload = {
        "model": "gpt-4-turbo",
        "messages": messages,
        "max_tokens": 500
    }

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"⚠️ *Resposta padrão:*\n\nRecebi sua mensagem! Como seu personal trainer virtual, recomendo foco, consistência e boa alimentação! 💪"
            
    except:
        return "💪 *Mensagem motivacional:*\n\nContinue firme nos treinos! Cada esforço conta! 🏋️‍♂️"

# ================== Z-API ==================
def enviar_mensagem(phone, text):
    url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{TOKEN_INSTANCIA}/send-text"

    headers = {
        "Client-Token": CLIENT_TOKEN,
        "Content-Type": "application/json"
    }

    payload = {"phone": phone, "message": text}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"📤 Z-API: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro Z-API: {e}")

# ================== TESTE ==================
@app.route("/teste", methods=["GET"])
def teste():
    """Rota para teste manual"""
    phone = request.args.get("phone", "553191316890")
    msg = request.args.get("msg", "Oi")
    
    resposta = tratar_texto(phone, msg)
    enviar_mensagem(phone, resposta)
    
    return f"✅ Teste enviado para {phone}"

# ================== START ==================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"\n{'='*60}")
    print("🤖 PERSONAL TRAINER BOT - INICIADO")
    print("="*60)
    print(f"📍 Porta: {port}")
    print(f"📱 Instance: {ZAPI_INSTANCE}")
    print(f"🔑 Token: {TOKEN_INSTANCIA[:10]}...")
    print(f"👤 Client Token: {CLIENT_TOKEN[:10]}...")
    print(f"🧠 OpenAI Key: {OPENAI_API_KEY[:10]}...")
    print("="*60)
    print("🌐 Webhook: /webhook")
    print("🧪 Teste: /teste?phone=553191316890&msg=Oi")
    print("="*60 + "\n")
    
    app.run(host="0.0.0.0", port=port, debug=False)
