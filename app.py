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

@app.route("/", methods=["GET"])
def index():
    return "🤖 Bot WhatsApp Online"

@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    if request.method == "GET":
        return "✅ Webhook OK", 200
    
    data = request.json
    
    # Ignora mensagens enviadas pelo próprio bot
    if data.get("fromMe"):
        return "Ignorado", 200
    
    phone = data.get("phone")
    message = data.get("text", {}).get("message")
    
    if phone and message:
        # Resposta simples e direta
        resposta = f"✅ Recebi sua mensagem!\n\nVocê disse: {message}\n\nEnviado em: {datetime.now().strftime('%H:%M:%S')}"
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
        print(f"📤 Resposta Z-API: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Bot iniciado na porta {port}")
    app.run(host="0.0.0.0", port=port)










from flask import Flask, request
import requests
import os
from datetime import datetime

app = Flask(__name__)

# ================== CONFIGURAÇÕES ==================
ZAPI_INSTANCE = os.environ.get "3EC42CD717B182BE009E5A8D44CAB450"
TOKEN_INSTANCIA = "C1C4D4B66FC02593FCCB149E"
CLIENT_TOKEN = os.environ.get "F0d19adbde8554463ab200473ded89ccbS"
OPENAI_API_KEY = os.environ.get "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"
# ===================================================

# ================== MEMÓRIA TEMPORÁRIA ==================
user_memory = {}
# =======================================================

@app.route("/", methods=["GET"])
def index():
    return "🤖 Bot Fitness Online"

@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    if request.method == "GET":
        return "Webhook OK", 200

    data = request.json
    print("📩 WEBHOOK:", data)

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
    text_lower = text.lower()

    if "treinei" in text_lower:
        registrar_treino(phone)
        return "🏋️ Treino registrado com sucesso!"

    if "relatório" in text_lower:
        return gerar_relatorio(phone)

    return responder_chatgpt(text)

# ================== TREINO ==================
def registrar_treino(phone):
    user_memory.setdefault(phone, {"treinos": [], "refeicoes": []})
    user_memory[phone]["treinos"].append(datetime.now().date().isoformat())

# ================== RELATÓRIO ==================
def gerar_relatorio(phone):
    dados = user_memory.get(phone)

    if not dados:
        return "❌ Ainda não tenho dados suficientes."

    prompt = f"""
    Gere um relatório motivador.
    Treinos registrados: {len(dados['treinos'])}
    Refeições analisadas: {len(dados['refeicoes'])}
    """

    return responder_chatgpt(prompt)

# ================== IMAGEM ==================
def analisar_imagem(image_url):
    prompt = """
    Analise a imagem enviada.

    Se for comida:
    - calorias estimadas
    - proteínas
    - carboidratos
    - gorduras

    Se for shape:
    - pontos fortes
    - pontos a melhorar
    - observações técnicas
    """

    return responder_chatgpt(prompt, image_url)

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
        "model": "gpt-4.1-mini",
        "messages": messages,
        "max_tokens": 500
    }

    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=30
    )

    return r.json()["choices"][0]["message"]["content"]

# ================== Z-API ==================
def enviar_mensagem(phone, text):
    url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/messages/send-text"

    headers = {
        "client-token": CLIENT_TOKEN,
        "Content-Type": "application/json"
    }

    payload = {"phone": phone, "message": text}

    r = requests.post(url, json=payload, headers=headers)
    print("📤 Z-API:", r.status_code, r.text)

# ================== START ==================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

