from flask import Flask, request
import requests
import os
from datetime import datetime

app = Flask(__name__)

# ================== CONFIG ==================
ZAPI_INSTANCE = "3EC42CD717B182BE009E5A8D44CAB450"
TOKEN_INSTANCIA = "C1C4D4B66FC02593FCCB149E"
CLIENT_TOKEN = "F0d19adbde8554463ab200473ded89ccbS"

# ⚠️ SUBSTITUA COM SUA CHAVE DA OPENAI PLATFORM!
# Acesse: https://platform.openai.com/api-keys
OPENAI_API_KEY = "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"
# ============================================

user_memory = {}

@app.route("/", methods=["GET"])
def index():
    return "🤖 Bot Online - Aguardando chave OpenAI"

@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    if request.method == "GET":
        return "✅", 200
    
    data = request.json
    
    if data.get("fromMe"):
        return "ok", 200

    phone = data.get("phone")
    nome = data.get("senderName", "Amigo")
    text = data.get("text", {}).get("message", "")
    image = data.get("image", {}).get("imageUrl")

    print(f"\n📩 {nome}: {text if text else '📸 Imagem'}")

    if OPENAI_API_KEY == "sk-sua-chave-openai-platform-aqui":
        # Se chave não foi configurada
        resposta = """🔑 *CONFIGURE SUA CHAVE OPENAI*

Para eu analisar suas fotos com IA:

1. Acesse: https://platform.openai.com
2. Crie conta (NÃO use email do ChatGPT)
3. Vá em "API Keys" → "Create new secret key"
4. Cole a chave no código do bot
5. Adicione US$5 em créditos

*Enquanto isso, como Personal Trainer:*
🏋️ Foco nos exercícios básicos
🥗 Proteína em todas as refeições
💧 3L de água por dia
🛌 8h de sono

*Você consegue!* 💪"""
    elif image:
        resposta = analisar_com_openai(image, nome)
    elif text:
        resposta = responder_texto(phone, nome, text)
    else:
        resposta = "Envie uma mensagem ou foto! 📸"
    
    enviar_mensagem(phone, resposta)
    return "ok", 200

def analisar_com_openai(image_url, nome):
    """Tenta usar OpenAI para análise"""
    
    # Primeiro verifica se a chave é válida
    if OPENAI_API_KEY.startswith("sk-proj-"):
        return """❌ *CHAVE INVÁLIDA DETECTADA*

Sua chave começa com `sk-proj-` (ChatGPT Team).

*Você precisa de uma chave da OpenAI Platform:*
1. Acesse: https://platform.openai.com/api-keys
2. Use email DIFERENTE do seu ChatGPT
3. Gere nova chave (começa com `sk-` normal)
4. Adicione créditos (US$5)
5. Substitua no código

*Dica do Personal Trainer enquanto isso:*
"A disciplina supera a motivação" 💪"""
    
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""Analise esta imagem como Personal Trainer e Nutricionista.

Usuário: {nome}

SE FOR COMIDA:
- Calorias estimadas
- Macronutrientes
- Pontos positivos
- Sugestões

SE FOR SHAPE/EXERCÍCIO:
- Pontos fortes
- Áreas para melhorar
- Exercícios recomendados
- Motivação

Seja positivo e técnico!"""
        
        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }],
            "max_tokens": 500
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        elif response.status_code == 401:
            return """🔐 *ERRO DE AUTENTICAÇÃO*

Sua chave OpenAI não é válida ou expirou.

*Solução:*
1. https://platform.openai.com/api-keys
2. Crie NOVA chave
3. Adicione créditos (US$5)
4. Substitua no código

*Lembre-se do treino:*
Consistência > Intensidade 💪"""
        else:
            return f"⚠️ Erro {response.status_code}. Configure chave OpenAI válida."
            
    except Exception as e:
        return f"""🤖 *ANÁLISE MANUAL DO PERSONAL TRAINER*

Vi sua foto! Como especialista, recomendo:

🎯 *PRINCÍPIOS BÁSICOS:*
1. Treino consistente 4-5x/semana
2. Dieta rica em proteínas
3. Hidratação constante
4. Descanso adequado

💪 *FOCO NO PROCESSO!*

(Para análise detalhada com IA, configure chave OpenAI)"""

def responder_texto(phone, nome, text):
    text = text.lower()
    
    if phone not in user_memory:
        user_memory[phone] = {"nome": nome, "treinos": 0}
        return f"""👋 Olá {nome}! Sou seu Personal Trainer IA.

*Configure chave OpenAI para:*
• Análise de fotos de comida
• Feedback do seu shape
• Dicas personalizadas

*Acesse:* https://platform.openai.com/api-keys

*Enquanto isso:* Foco, Fé e Força! 💪"""
    
    if "treinei" in text:
        user_memory[phone]["treinos"] += 1
        return f"""✅ TREINO {user_memory[phone]['treinos']} REGISTRADO!

Parabéns, {nome}! Continue assim!

"Dias difíceis criam corpos fortes" 💪"""
    
    return f"""💬 Entendi, {nome}!

Você disse: "{text}"

*Como Personal Trainer, lembro:*
- Progresso vem com consistência
- Cada treino conta
- Sua saúde é prioridade

Configure OpenAI para respostas com IA! 🧠"""

def enviar_mensagem(phone, text):
    url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{TOKEN_INSTANCIA}/send-text"
    headers = {"Client-Token": CLIENT_TOKEN, "Content-Type": "application/json"}
    payload = {"phone": phone, "message": text}
    
    try:
        requests.post(url, json=payload, headers=headers, timeout=5)
        print(f"✅ Enviado para {phone}")
    except:
        print("❌ Erro ao enviar")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"\n🤖 Bot na porta {port}")
    
    if OPENAI_API_KEY.startswith("sk-proj-"):
        print("❌ CHAVE ERRADA: sk-proj- (use OpenAI Platform)")
    elif OPENAI_API_KEY == "sk-sua-chave-openai-platform-aqui":
        print("⚠️ Configure sua chave OpenAI!")
    else:
        print(f"✅ Chave OpenAI: {OPENAI_API_KEY[:15]}...")
    
    print("🔗 Webhook: /webhook")
    app.run(host="0.0.0.0", port=port)
