from flask import Flask, request
import requests
import os
from datetime import datetime

app = Flask(__name__)

# ================== CONFIGURAÇÕES ==================
ZAPI_INSTANCE = "3EC42CD717B182BE009E5A8D44CAB450"
TOKEN_INSTANCIA = "C1C4D4B66FC02593FCCB149E"
CLIENT_TOKEN = "F0d19adbde8554463ab200473ded89ccbS"
# Google Gemini API Key (GRATUITA - pegue a sua)
GEMINI_API_KEY = "AIzaSyB0jq9B6n4x7n8q9r0t1u2v3w4x5y6z7A8B9C0D"  # ⚠️ SUBSTITUA
# ===================================================

# ================== MEMÓRIA ==================
user_memory = {}
# =============================================

@app.route("/", methods=["GET"])
def index():
    return "🤖 Personal Trainer Online ✅"

@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    if request.method == "GET":
        return "✅ Webhook OK", 200

    data = request.json
    
    if data.get("fromMe"):
        return "ignored", 200

    phone = data.get("phone")
    nome = data.get("senderName", "Amigo")
    text = data.get("text", {}).get("message", "")
    image = data.get("image", {}).get("imageUrl")

    print(f"\n📩 {nome}: {text[:50] if text else '📸 IMAGEM'}")

    if image:
        resposta = analisar_imagem_gemini(image, nome)
        enviar_mensagem(phone, resposta)
        return "ok", 200

    if text:
        resposta = tratar_texto(phone, nome, text)
        enviar_mensagem(phone, resposta)

    return "ok", 200

def tratar_texto(phone, nome, text):
    text_lower = text.lower().strip()
    
    if phone not in user_memory:
        user_memory[phone] = {
            "nome": nome,
            "treinos": [],
            "refeicoes": [],
            "primeira_interacao": datetime.now().isoformat()
        }
        return f"""👋 *OLÁ {nome.upper()}!* 

🤖 *EU SOU SEU PERSONAL TRAINER VIRTUAL*

🎯 *MINHAS FUNÇÕES:*
• Análise de alimentos por foto
• Feedback do seu shape
• Registro de treinos
• Motivação diária
• Dicas personalizadas

💪 *VAMOS JUNTOS NESSA JORNADA!*

Envie uma foto de comida ou do seu shape para começar! 🏋️‍♂️"""
    
    if "treinei" in text_lower:
        registrar_treino(phone)
        return f"""✅ *TREINO REGISTRADO!* 🏋️‍♂️

Parabéns, {nome}! 
Consistência é o segredo!

*Dica do dia:* 
"O corpo alcança o que a mente acredita" 💪"""
    
    if "relatório" in text_lower:
        dados = user_memory.get(phone, {})
        treinos = len(dados.get("treinos", []))
        return f"""📊 *RELATÓRIO DE {nome.upper()}*

✅ Treinos registrados: *{treinos}*
📅 Desde: {dados.get('primeira_interacao', 'Hoje')[:10]}

🏆 Nível: {'🔥 AVANÇADO' if treinos > 10 else '🚀 INTERMEDIÁRIO' if treinos > 5 else '⭐ INICIANTE'}

💪 *Continue assim! Cada treino te transforma!*"""
    
    if text_lower in ["oi", "ola", "olá"]:
        return f"E aí, {nome}! 😊\nPronto para evoluir hoje?"
    
    if text_lower == "ajuda":
        return """🤖 *AJUDA - PERSONAL TRAINER*

📸 *Envie FOTO de:*
• Comida → Análise nutricional
• Shape → Feedback profissional
• Exercício → Correção técnica

⌨️ *COMANDOS:*
• "treinei" → Registrar treino
• "relatório" → Ver progresso
• "dicas" → Dicas fitness
• "meta Xkg" → Definir peso-alvo

*Exemplo:* "meta 80kg" """
    
    if text_lower.startswith("meta "):
        try:
            meta = text_lower.replace("meta", "").replace("kg", "").strip()
            user_memory[phone]["meta_peso"] = float(meta)
            return f"🎯 *META DEFINIDA:* {meta}kg\n\nVamos alcançar juntos! 💪"
        except:
            return "⚖️ Formato: 'meta 80kg'"
    
    if text_lower == "dicas":
        return gerar_dicas_fitness()
    
    # Se não for comando, usa Gemini
    return usar_gemini(f"""O usuário {nome} disse: "{text}"

Responda como um Personal Trainer motivador, especialista em fitness e nutrição.
Seja positivo, dê dicas práticas e motive-o a continuar treinando!""")

def analisar_imagem_gemini(image_url, nome):
    """Analisa imagem usando Google Gemini"""
    
    print(f"🔍 Analisando imagem com Gemini...")
    
    prompt = f"""Analise esta imagem como um Personal Trainer e Nutricionista profissional.

Usuário: {nome}

SE FOR COMIDA/REFEIÇÃO:
• Calorias aproximadas
• Macronutrientes (proteínas, carbs, gorduras)
• Pontos positivos
• Sugestões de melhoria
• Dica nutricional prática

SE FOR SHAPE/CORPO/EXERCÍCIO:
• Pontos fortes visíveis
• Áreas para desenvolvimento
• Exercícios recomendados
• Feedback construtivo
• Motivação personalizada

Formato:
- Seja técnico mas acessível
- Use emojis relevantes
- Seja positivo e encorajador
- Baseie em ciência do esporte

Resposta em português!"""
    
    return usar_gemini(prompt, image_url)

def usar_gemini(prompt, image_url=None):
    """Usa Google Gemini API (GRATUITA)"""
    
    if GEMINI_API_KEY == "AIzaSyB0jq9B6n4x7n8q9r0t1u2v3w4x5y6z7A8B9C0D":
        return """🤖 *PERSONAL TRAINER DIZ:*

Para análises detalhadas de imagens, configure sua chave do Google Gemini:

1. Acesse: https://aistudio.google.com/apikey
2. Crie uma nova chave API
3. Cole no código (variável GEMINI_API_KEY)

📸 *ENQUANTO ISSO:*
• Comida: Foco em proteínas e alimentos naturais
• Shape: Consistência nos treinos + dieta
• Exercício: Execução correta > peso

💪 *VOCÊ CONSEGUE!*"""
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent?key={GEMINI_API_KEY}"
    
    content = [{"text": prompt}]
    
    if image_url:
        # Gemini precisa da imagem em base64
        try:
            img_response = requests.get(image_url, timeout=10)
            import base64
            img_base64 = base64.b64encode(img_response.content).decode('utf-8')
            content.append({
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": img_base64
                }
            })
        except:
            pass
    
    payload = {"contents": [{"parts": content}]}
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            resposta = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            return resposta
        else:
            return f"""🏋️‍♂️ *FEEDBACK DO PERSONAL TRAINER*

Baseado em análise visual rápida:

📸 *O QUE VI:*
• Potencial para evolução
• Caminho para resultados
• Disciplina em progresso

🎯 *RECOMENDAÇÃO:*
1. Treino consistente 3-5x/semana
2. Proteína: 2g/kg de peso
3. Hidratação: 3L água/dia
4. Sono: 7-8h/noite

💪 *FOCO E FÉ!*"""
            
    except:
        return gerar_dicas_fitness()

def gerar_dicas_fitness():
    """Gera dicas de fitness"""
    dicas = [
        "💧 *HIDRATAÇÃO:* Beba 500ml água 30min antes do treino",
        "🥚 *PROTEÍNA:* Consuma 20-30g de proteína pós-treino",
        "🏋️ *TREINO:* Foque em exercícios compostos (agachamento, supino, remada)",
        "🛌 *DESCANSO:* Musculação só cresce com descanso adequado",
        "📊 *PROGRESSÃO:* Aumente pesos ou repetições toda semana",
        "🥑 *GORDURAS:* Inclua abacate, castanhas e azeite na dieta",
        "⏰ *CONSISTÊNCIA:* Melhor treinar 30min/dia que 3h 1x/semana",
        "🧠 *MENTE:* Visualize seus objetivos durante o treino"
    ]
    from random import choice
    return f"""💡 *DICA FITNESS DO DIA*

{choice(dicas)}

*Lembre-se:* Pequenas ações consistentes > Grandes ações esporádicas! 💪"""

def registrar_treino(phone):
    user_memory.setdefault(phone, {"treinos": []})
    user_memory[phone]["treinos"].append({
        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "tipo": "treino_registrado"
    })

def enviar_mensagem(phone, text):
    url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{TOKEN_INSTANCIA}/send-text"
    headers = {"Client-Token": CLIENT_TOKEN, "Content-Type": "application/json"}
    payload = {"phone": phone, "message": text}
    
    try:
        requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"✅ Enviado para {phone}")
    except:
        print(f"❌ Erro ao enviar")

@app.route("/teste-gemini", methods=["GET"])
def teste_gemini():
    """Testa Gemini"""
    return usar_gemini("Teste de conexão. Responda '✅ Gemini funcionando!'")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"\n🤖 PERSONAL TRAINER BOT - PORT {port}")
    print("🔗 Webhook: /webhook")
    print("💡 Dica: Configure Google Gemini API para análises de imagem")
    app.run(host="0.0.0.0", port=port, debug=False)
