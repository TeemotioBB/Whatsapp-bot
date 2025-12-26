from flask import Flask, request
import requests
import os
from datetime import datetime
import base64
import json

app = Flask(__name__)

# ================== CONFIGURAÇÕES ==================
ZAPI_INSTANCE = "3EC42CD717B182BE009E5A8D44CAB450"
TOKEN_INSTANCIA = "C1C4D4B66FC02593FCCB149E"
CLIENT_TOKEN = "F0d19adbde8554463ab200473ded89ccbS"
OPENAI_API_KEY = "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"
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
    print(f"\n📩 Mensagem recebida: {data.get('text', {}).get('message', '')[:50] if data.get('text') else 'IMAGEM'}...")

    if data.get("fromMe"):
        return "ignored", 200

    phone = data.get("phone")
    nome = data.get("senderName", "Amigo")
    text = data.get("text", {}).get("message", "")
    image = data.get("image", {}).get("imageUrl")

    if image:
        print(f"📸 Imagem recebida: {image[:100]}...")
        resposta = analisar_imagem_com_openai(image)
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
        return responder_openai(f"""O usuário {nome} acabou de iniciar conversa. 
        Apresente-se como um Personal Trainer Virtual motivador e profissional.
        Diga que pode ajudar com: treinos, análise de comida via fotos, feedback de shape e motivação.
        Seja acolhedor e empolgado!""")

    if "treinei" in text_lower:
        registrar_treino(phone)
        return responder_openai(f"""O usuário {nome} acabou de registrar um treino.
        Parabenize-o pelo comprometimento e dê uma dica motivacional sobre consistência nos treinos.
        Seja energético e positivo!""")

    if "relatório" in text_lower:
        dados = user_memory.get(phone, {})
        treinos = len(dados.get("treinos", []))
        return responder_openai(f"""Gere um relatório motivacional para {nome}.
        Ele já registrou {treinos} treinos.
        Dê feedback positivo, mostre progresso e incentive a continuar.
        Seja detalhado e inspirador!""")
    
    if text_lower == "ajuda":
        return """🤖 *COMANDOS DO PERSONAL TRAINER*

🏋️ *"treinei"* - Registrar treino
📊 *"relatório"* - Ver progresso  
🥗 *Envie foto* - Análise de comida
💪 *Envie foto* - Feedback do shape
💬 *Converse normalmente* - Dicas personalizadas

*Estou aqui para sua evolução!* 💪"""
    
    # Usa OpenAI para outras mensagens
    return responder_openai(f"""O usuário {nome} disse: "{text}"
    
    Responda como um Personal Trainer Virtual especializado em fitness, nutrição e motivação.
    Seja:
    1. Positivo e encorajador
    2. Prático e objetivo  
    3. Baseado em ciência do esporte
    4. Motivacional
    
    Dê dicas úteis relacionadas ao que ele disse!""")

def registrar_treino(phone):
    user_memory.setdefault(phone, {"treinos": []})
    user_memory[phone]["treinos"].append({
        "data": datetime.now().strftime("%d/%m/%Y %H:%M")
    })

def analisar_imagem_com_openai(image_url):
    """Analisa imagem usando OpenAI GPT-4 Vision"""
    
    print(f"🔍 Analisando imagem com OpenAI...")
    
    prompt = """Analise esta imagem como um Personal Trainer e Nutricionista profissional:

1. SE FOR COMIDA/REFEIÇÃO:
   - Calorias aproximadas
   - Proteínas, carboidratos, gorduras estimados
   - Pontos positivos e negativos
   - Sugestão de melhoria (se necessário)
   - Dica nutricional relacionada

2. SE FOR SHAPE/CORPO/EXERCÍCIO:
   - Pontos fortes visíveis
   - Áreas que podem melhorar
   - Dica de exercício específico
   - Feedback construtivo
   - Motivação personalizada

3. SE FOR OUTRA COISA:
   - Relacione com fitness se possível
   - Dê uma dica motivacional sobre saúde

Seja:
• Técnico mas acessível
• Construtivo e positivo  
• Baseado em ciência
• Motivacional

Formate a resposta com emojis e seja entusiasta!"""
    
    return responder_openai(prompt, image_url)

def responder_openai(prompt, image_url=None):
    """Chama OpenAI API com tratamento de erros detalhado"""
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Prepara mensagens
    messages = [{"role": "user", "content": []}]
    
    # Adiciona texto
    messages[0]["content"].append({
        "type": "text",
        "text": prompt
    })
    
    # Adiciona imagem se existir
    if image_url:
        print(f"🖼️ Adicionando imagem ao prompt: {image_url[:50]}...")
        messages[0]["content"].append({
            "type": "image_url",
            "image_url": {
                "url": image_url,
                "detail": "high"
            }
        })
    
    payload = {
        "model": "gpt-4-vision-preview",  # Modelo específico para visão
        "messages": messages,
        "max_tokens": 1000,
        "temperature": 0.7
    }
    
    print(f"📡 Enviando para OpenAI...")
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=45
        )
        
        print(f"📊 OpenAI Status: {response.status_code}")
        
        if response.status_code == 200:
            resposta = response.json()["choices"][0]["message"]["content"]
            print(f"✅ OpenAI respondeu: {resposta[:100]}...")
            return resposta
            
        elif response.status_code == 401:
            print("❌ ERRO 401: Chave OpenAI inválida ou expirada")
            return "🔑 *Ops!* Parece que meu acesso à inteligência artificial está temporariamente limitado.\n\nMas como seu Personal Trainer, posso te dizer: Foco nos treinos, dieta limpa e consistência são a chave! 💪"
            
        elif response.status_code == 429:
            print("❌ ERRO 429: Limite de requisições excedido")
            return "⏳ *Estou processando muitas análises!*\n\nEnquanto isso: Mantenha a proteína alta, os treinos intensos e o descanso em dia! 🏋️‍♂️"
            
        else:
            print(f"❌ ERRO OpenAI {response.status_code}: {response.text}")
            return f"""🏋️‍♂️ *Como seu Personal Trainer, recomendo:*

1. *Para alimentação:* Foco em proteínas magras, carboidratos complexos e gorduras boas
2. *Para treino:* Consistência > Intensidade, progressão de cargas
3. *Para resultados:* Paciência + Disciplina = Sucesso

*Continue firme!* Cada dia conta! 💪"""
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout na OpenAI")
        return "⏳ *Análise demorando um pouco...*\n\nEnquanto isso, lembre-se: O progresso vem da consistência! 💪"
        
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")
        return """🤖 *Personal Trainer Virtual diz:*

Sua dedicação é o que mais importa! 
• Treine com inteligência
• Alimente-se com consciência  
• Descanse com qualidade
• Repita com consistência

*Você consegue!* 🚀"""

def enviar_mensagem(phone, text):
    """Envia mensagem via Z-API"""
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

@app.route("/teste-openai", methods=["GET"])
def teste_openai():
    """Testa a conexão com OpenAI"""
    try:
        resposta = responder_openai("Olá! Teste de conexão. Responda apenas '✅ OpenAI funcionando!'")
        return f"OpenAI: {resposta}"
    except Exception as e:
        return f"Erro OpenAI: {str(e)}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"\n{'='*70}")
    print("🤖 PERSONAL TRAINER BOT COM OPENAI")
    print("="*70)
    print(f"📍 Porta: {port}")
    print(f"🔑 OpenAI Key: {OPENAI_API_KEY[:20]}...")
    print(f"📱 Teste OpenAI: /teste-openai")
    print("="*70)
    print("🚀 *Dica:* Sua chave OpenAI pode precisar de:")
    print("   1. Créditos na conta")
    print("   2. Acesso à API GPT-4 Vision")
    print("   3. Atualização se for uma chave antiga")
    print("="*70)
    
    app.run(host="0.0.0.0", port=port, debug=False)
