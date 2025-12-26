from flask import Flask, request
import requests
import os
from datetime import datetime

app = Flask(__name__)

# ================== CONFIG ==================
ZAPI_INSTANCE = "3EC42CD717B182BE009E5A8D44CAB450"
TOKEN_INSTANCIA = "C1C4D4B66FC02593FCCB149E"
CLIENT_TOKEN = "F0d19adbde8554463ab200473ded89ccbS"

# ⚠️ SUBSTITUA COM SUA CHAVE DA XAI (GROK)!
# Acesse: https://console.x.ai/ (crie uma conta na xAI)
GROK_API_KEY = "xai-7KMFujAXXKvr9khsd9qSYrrllqlViTpeYY1hF4N3zLmylAvlpwFHRV53Z9l68EijuL72GA6Jtg6TQXUz"  # Substitua com sua chave real
# ============================================

user_memory = {}

@app.route("/", methods=["GET"])
def index():
    return "🤖 Bot Online - Aguardando chave xAI Grok"

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

    if GROK_API_KEY == "xai-sua-chave-grok-aqui":
        # Se chave não foi configurada
        resposta = """🔑 *CONFIGURE SUA CHAVE GROK (xAI)*

Para eu analisar suas fotos com IA:

1. Acesse: https://console.x.ai/
2. Crie uma conta na xAI
3. Vá em "API Keys" → "Create new key"
4. Cole a chave no código do bot
5. Adicione créditos se necessário

*Enquanto isso, como Personal Trainer:*
🏋️ Foco nos exercícios básicos
🥗 Proteína em todas as refeições
💧 3L de água por dia
🛌 8h de sono

*Você consegue!* 💪"""
    elif image:
        resposta = analisar_com_grok(image, nome, text)
    elif text:
        resposta = responder_texto(phone, nome, text)
    else:
        resposta = "Envie uma mensagem ou foto! 📸"
    
    enviar_mensagem(phone, resposta)
    return "ok", 200

def analisar_com_grok(image_url, nome, text_prompt=""):
    """Tenta usar Grok API para análise de imagem"""
    
    if GROK_API_KEY == "xai-sua-chave-grok-aqui":
        return """❌ *CHAVE GROK NÃO CONFIGURADA*

Para usar análise de imagens com Grok:

1. Acesse: https://console.x.ai/
2. Crie uma conta na xAI
3. Gere sua chave API
4. Cole no código
5. Ative o suporte a visão (se necessário)

*Dica do Personal Trainer:*
"A consistência é a chipe do sucesso" 💪"""
    
    try:
        headers = {
            "Authorization": f"Bearer {GROK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Construir o prompt baseado no texto enviado (se houver)
        base_prompt = f"""Analise esta imagem como um Personal Trainer e Nutricionista especializado.

Usuário: {nome}

"""
        
        if text_prompt:
            user_question = text_prompt
        else:
            user_question = "O que você vê nesta imagem? Analise como um personal trainer."
        
        full_prompt = f"""{base_prompt}
Usuário pergunta: "{user_question}"

SE FOR COMIDA/REFEIÇÃO:
- Estime calorias totais
- Analise macronutrientes (proteínas, carboidratos, gorduras)
- Pontos positivos da refeição
- Sugestões de melhorias
- Como isso se encaixa em uma dieta fitness

SE FOR FOTO DO CORPO/EXERCÍCIO:
- Avalie postura/forma
- Pontos fortes visíveis
- Áreas para desenvolvimento
- Sugestões de exercícios específicos
- Motivação personalizada

SE FOR AMBIENTE DE TREINO:
- Avalie equipamentos/ambiente
- Sugestões de otimização
- Rotinas recomendadas

SEJA:
1. Técnico mas acessível
2. Positivo e motivador
3. Prático com ações concretas
4. Breve mas completo

Responda em português do Brasil."""

        # Preparar o payload para Grok API
        # Nota: Verifique na documentação oficial se o Grok tem suporte a visão
        payload = {
            "model": "grok-beta",  # Verifique o modelo correto na documentação
            "messages": [
                {
                    "role": "user",
                    "content": full_prompt
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        # Se o Grok suportar visão diretamente, ajuste o payload:
        if "vision" in GROK_API_KEY or True:  # Remova o True quando confirmar
            # Formato para visão (ajuste conforme documentação oficial)
            payload = {
                "model": "grok-vision-beta",  # Modelo hipotético para visão
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": full_prompt},
                            {"type": "image_url", "image_url": {"url": image_url}}
                        ]
                    }
                ],
                "max_tokens": 1000
            }
        
        # Endpoint da API Grok (verifique na documentação oficial)
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",  # Endpoint oficial da xAI
            headers=headers,
            json=payload,
            timeout=45
        )
        
        print(f"Status Grok: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        elif response.status_code == 401:
            return """🔐 *ERRO DE AUTENTICAÇÃO GROK*

Sua chave xAI não é válida ou expirou.

*Solução:*
1. https://console.x.ai/
2. Verifique sua chave API
3. Renove se necessário
4. Verifique os créditos

*Lembre-se do treino:*
Progresso vem da consistência diária! 💪"""
            
        elif response.status_code == 429:
            return """⚠️ *LIMITE DE REQUISIÇÕES ATINGIDO*

A API Grok atingiu o limite de requisições.

*Solução:*
1. Aguarde alguns minutos
2. Verifique seu plano na xAI
3. Considere upgrade se necessário

*Dica do treino:* Persistência é tudo!"""
            
        else:
            return f"""🤖 *ANÁLISE MANUAL DO PERSONAL TRAINER*

Vi sua foto! Enquanto resolvemos a análise com IA:

🎯 *PRINCÍPIOS FUNDAMENTAIS:*
1. Treino consistente > treino perfeito
2. Proteína em todas as refeições
3. Hidratação: 35ml por kg corporal
4. Sono: 7-9h por noite

💪 *FOCO NO PROCESSO!*

(Erro técnico: {response.status_code}. Configure chave Grok corretamente)"""

    except requests.exceptions.Timeout:
        return """⏱️ *TEMPO ESGOTADO*

A análise está demorando mais que o normal.

*Enquanto isso, lembre-se:*
"A paciência é uma virtude no fitness"
Continue seguindo sua rotina! 💪"""

    except Exception as e:
        print(f"Erro Grok: {str(e)}")
        return f"""🤖 *ANÁLISE PERSONAL TRAINER*

Baseado na sua foto e experiência geral:

🏋️ *PARA QUALQUER TREINO:*
1. Execute o movimento completo
2. Mantenha a postura correta
3. Respiração consciente
4. Progressão gradual

🥗 *PARA NUTRIÇÃO:*
- Proteínas magras primeiro
- Carboidratos complexos
- Gorduras saudáveis
- Vegetais coloridos

*Erro técnico:* Configure corretamente a chave Grok em https://console.x.ai/"""

def responder_texto(phone, nome, text):
    text_lower = text.lower()
    
    if phone not in user_memory:
        user_memory[phone] = {"nome": nome, "treinos": 0, "ultima_consulta": datetime.now().isoformat()}
        return f"""👋 Olá {nome}! Sou seu Personal Trainer com IA Grok.

*Configure chave Grok (xAI) para:*
• Análise avançada de fotos de comida
• Feedback preciso do seu shape
• Dicas personalizadas com IA

*Acesse:* https://console.x.ai/

*Comandos disponíveis:*
• "treinei hoje" - Registrar treino
• "dieta" - Dicas nutricionais
• "exercício" - Sugestões de treino

Foco, Fé e Força! 💪"""
    
    # Registrar treino
    if any(word in text_lower for word in ["treinei", "malhei", "treino", "academia"]):
        user_memory[phone]["treinos"] += 1
        user_memory[phone]["ultima_consulta"] = datetime.now().isoformat()
        count = user_memory[phone]["treinos"]
        
        return f"""✅ TREINO #{count} REGISTRADO!

Parabéns, {nome}! Cada sessão conta.

*Lembre-se hoje:*
1. Hidratação adequada
2. Alimentação pós-treino
3. Descanso ativo

"Dias difíceis criam corpos fortes" 💪"""
    
    # Dicas nutricionais
    elif any(word in text_lower for word in ["dieta", "comer", "alimentação", "proteína"]):
        return f"""🥗 *DIETA FITNESS - {nome.upper()}*

*PRINCÍPIOS BÁSICOS:*
1. Proteína: 2g por kg corporal
2. Carboidratos: 3-5g por kg
3. Gorduras: 0.8-1g por kg
4. Fibras: 30-40g diárias

*REFEIÇÕES:* 4-6 por dia

Configure Grok para análise personalizada!"""
    
    # Exercícios
    elif any(word in text_lower for word in ["exercício", "treinar", "musculação", "cardio"]):
        return f"""🏋️ *TREINO DO DIA - {nome.upper()}*

*A) Aquecimento (10min)*
- Mobilidade articular
- Cardio leve

*B) Treino Principal*
- Agachamento: 4x10
- Supino: 4x8
- Remada: 4x10
- Abdominal: 3x15

*C) Alongamento (5min)*

*Configure Grok para plano personalizado!*"""
    
    # Conversa normal
    else:
        return f"""💬 Entendi, {nome}!

Você disse: "{text}"

*Como Personal Trainer, lembro:*
- Progresso = Consistência × Tempo
- Cada escolha alimentar importa
- Seu corpo responde ao hábito

*Configure Grok (xAI) para respostas com IA avançada!* 🧠

Acesse: https://console.x.ai/"""

def enviar_mensagem(phone, text):
    url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{TOKEN_INSTANCIA}/send-text"
    headers = {"Client-Token": CLIENT_TOKEN, "Content-Type": "application/json"}
    payload = {"phone": phone, "message": text}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            print(f"✅ Enviado para {phone}")
        else:
            print(f"❌ Erro {response.status_code} ao enviar")
    except Exception as e:
        print(f"❌ Erro de conexão: {str(e)}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"\n🤖 Bot Personal Trainer com Grok IA")
    print(f"🌐 Porta: {port}")
    
    # Verificação da chave Grok
    if GROK_API_KEY == "xai-sua-chave-grok-aqui":
        print("⚠️ CONFIGURE SUA CHAVE GROK (xAI)!")
        print("🔗 Acesse: https://console.x.ai/")
    elif GROK_API_KEY.startswith("xai-"):
        print(f"✅ Chave Grok detectada: {GROK_API_KEY[:20]}...")
    else:
        print(f"🔑 Chave configurada: {GROK_API_KEY[:15]}...")
    
    print("🔗 Webhook: /webhook")
    print("📱 Aguardando mensagens...")
    app.run(host="0.0.0.0", port=port, debug=False)
