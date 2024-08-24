import paho.mqtt.client as mqtt
import telebot
import aiohttp
import asyncio
import json
import requests
from datetime import datetime
import pytz
import threading
import time  # Importar o módulo time

# Configuração da chave de serviço do Zoho CRM para WhatsApp
zoho_service_config = {
    "connectionLinkName": "whats",
    "connectionName": "https://web.whatsapp.com/",
    "serviceName": "zoho_crm",
    "userAccess": False,
    "isUserDefinedService": False,
    "sharedBy": "858219855"
}

# Dados do MQTT
broker_address = "127.0.0.1"  # Altere conforme necessário
port = 1883
topic_temperatura = "casa/sensor/temperatura"
topic_alarme = "casa/alarme"
topic_tomada = "casa/tomada"

# Dados do Telegram
bot_token = "7317730995:AAGjg46Gn4ycopouh1iA6zeLKlLaXPd26uU"
chat_id = "2006035577"

# Dados da API de Pesquisa Customizada do Google
google_api_key = "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"
google_cx = "f6efec510e71c46b0"

# Limite de temperatura
limite_temperatura_superior = 25
limite_temperatura_inferior = 18

# Simulação de tomada
tomada_ligada = False

# Lista de lembretes
lembretes = []

# Inicializar o bot do Telegram
bot = telebot.TeleBot(bot_token)

# Inicializar o cliente MQTT
client = mqtt.Client()

async def get_clima():
    """Obtém a informação do clima da cidade configurada."""
    api_key = '45c496166f8794f57c7d97973ec13097'
    cidade = 'Ituverava, BR'
    url = f'http://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={api_key}&units=metric'

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.text()
            clima = json.loads(data)

            if 'weather' in clima and 'main' in clima:
                descricao = clima['weather'][0]['description']
                temperatura = clima['main']['temp']
                return f"Clima em {cidade}: {descricao}, {temperatura:.1f}°C"
            else:
                return "Não consegui obter a informação do clima no momento."

def buscar_no_google(query, api_key, cx):
    """Realiza uma pesquisa no Google e retorna os resultados."""
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={cx}"
    try:
        response = requests.get(url)
        results = response.json()

        if 'items' in results:
            resposta = ""
            for item in results['items']:
                resposta += f"Título: {item['title']}\nLink: {item['link']}\n\n"
            return resposta
        else:
            return "Nenhum resultado encontrado no Google."
    except requests.RequestException as e:
        return f"Erro na pesquisa Google: {e}"

def buscar_na_wikipedia(query):
    """Realiza uma pesquisa na Wikipedia e retorna os resultados."""
    url = f"https://pt.wikipedia.org/w/api.php?action=query&format=json&list=search&srsearch={query}"
    try:
        response = requests.get(url)
        results = response.json()

        if 'query' in results and 'search' in results['query']:
            resposta = ""
            for item in results['query']['search']:
                title = item['title']
                snippet = item['snippet']
                resposta += f"Título: {title}\nResumo: {snippet}\nLink: https://pt.wikipedia.org/wiki/" + title.replace(" ", "_") + "\n\n"
            return resposta
        else:
            return "Nenhum resultado encontrado na Wikipedia."
    except requests.RequestException as e:
        return f"Erro na pesquisa Wikipedia: {e}"

def obter_hora_brasilia():
    """Obtém a hora atual no fuso horário de Brasília (GMT-3)."""
    tz_brasilia = pytz.timezone('America/Sao_Paulo')
    agora = datetime.now(tz_brasilia)
    return agora.strftime("%H:%M:%S")

def obter_dia_atual():
    """Obtém o dia da semana atual no fuso horário de Brasília."""
    tz_brasilia = pytz.timezone('America/Sao_Paulo')
    agora = datetime.now(tz_brasilia)
    return agora.strftime("%A, %d de %B de %Y")

def on_connect(client, userdata, flags, rc):
    """Callback para quando a conexão com o broker MQTT for estabelecida."""
    print("Conectado ao MQTT broker")
    client.subscribe(topic_temperatura)

def on_message(client, userdata, msg):
    """Callback para quando uma mensagem for recebida no tópico especificado."""
    if msg.topic == topic_temperatura:
        temperatura = float(msg.payload.decode())
        print(f"Temperatura: {temperatura:.1f}°C")

        if temperatura > limite_temperatura_superior:
            enviar_alarme(f"Temperatura alta: {temperatura:.1f}°C")
            ligar_tomada()
        elif temperatura < limite_temperatura_inferior:
            enviar_alarme(f"Temperatura baixa: {temperatura:.1f}°C")
            desligar_tomada()

def enviar_mensagem(mensagem, chat_id=chat_id):
    """Envia uma mensagem para o chat do Telegram."""
    try:
        # Dividir a mensagem em partes menores se necessário
        while len(mensagem) > 4096:
            parte = mensagem[:4096]
            bot.send_message(chat_id, parte)
            mensagem = mensagem[4096:]
        bot.send_message(chat_id, mensagem)
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

def enviar_alarme(mensagem):
    """Envia uma mensagem de alarme para o chat do Telegram."""
    enviar_mensagem(f"**ALARME!** {mensagem}")

def ligar_tomada():
    """Simula ligar a tomada e envia mensagem no chat do Telegram."""
    global tomada_ligada
    tomada_ligada = True
    print("Tomada ligada")
    enviar_mensagem("Tomada foi ligada.")

def desligar_tomada():
    """Simula desligar a tomada e envia mensagem no chat do Telegram."""
    global tomada_ligada
    tomada_ligada = False
    print("Tomada desligada")
    enviar_mensagem("Tomada foi desligada.")

@bot.message_handler(commands=['ligar'])
def ligar(mensagem):
    """Responde ao comando '/ligar' e simula ligar a tomada."""
    ligar_tomada()
    enviar_mensagem("A tomada foi ligada.", mensagem.chat.id)

@bot.message_handler(commands=['desligar'])
def desligar(mensagem):
    """Responde ao comando '/desligar' e simula desligar a tomada."""
    desligar_tomada()
    enviar_mensagem("A tomada foi desligada.", mensagem.chat.id)

@bot.message_handler(commands=['clima'])
def clima(mensagem):
    """Responde ao comando '/clima' e busca a informação do clima."""
    asyncio.run(handle_clima(mensagem))

async def handle_clima(mensagem):
    """Busca a informação do clima de forma assíncrona e envia a mensagem."""
    clima_info = await get_clima()
    enviar_mensagem(clima_info, mensagem.chat.id)

@bot.message_handler(commands=['pesquisar'])
def pesquisar(mensagem):
    """Responde ao comando '/pesquisar' e busca informações no Google e na Wikipedia."""
    query = mensagem.text[len('/pesquisar '):]
    google_result = buscar_no_google(query, google_api_key, google_cx)
    wikipedia_result = buscar_na_wikipedia(query)
    resultado = f"**Google:**\n{google_result}\n\n**Wikipedia:**\n{wikipedia_result}"
    enviar_mensagem(resultado, mensagem.chat.id)

@bot.message_handler(commands=['hora'])
def hora(mensagem):
    """Responde ao comando '/hora' com a hora atual no fuso horário de Brasília."""
    hora_atual = obter_hora_brasilia()
    enviar_mensagem(f"A hora atual em Brasília é: {hora_atual}", mensagem.chat.id)

@bot.message_handler(commands=['dia'])
def dia(mensagem):
    """Responde ao comando '/dia' com o dia atual no fuso horário de Brasília."""
    dia_atual = obter_dia_atual()
    enviar_mensagem(f"Hoje é: {dia_atual}", mensagem.chat.id)

@bot.message_handler(commands=['adicionar_lembrete'])
def adicionar_lembrete(mensagem):
    """Adiciona um lembrete à lista de lembretes."""
    try:
        texto = mensagem.text[len('/adicionar_lembrete '):]
        if ' | ' in texto:
            mensagem_lembrete, data_hora_str = texto.split(' | ')
            data_hora = datetime.strptime(data_hora_str, "%Y-%m-%d %H:%M:%S")
            data_hora = pytz.timezone('America/Sao_Paulo').localize(data_hora)  # Localize a data e hora

            lembrete = {
                "mensagem": mensagem_lembrete,
                "data_hora": data_hora,
                "chat_id": mensagem.chat.id
            }
            lembretes.append(lembrete)
            enviar_mensagem("Lembrete adicionado com sucesso.", mensagem.chat.id)
        else:
            enviar_mensagem("Formato inválido. Use: /adicionar_lembrete [mensagem] | [YYYY-MM-DD HH:MM:SS]", mensagem.chat.id)
    except Exception as e:
        enviar_mensagem(f"Erro ao adicionar lembrete: {e}", mensagem.chat.id)

@bot.message_handler(commands=['listar_lembretes'])
def listar_lembretes(mensagem):
    """Lista todos os lembretes."""
    if lembretes:
        resposta = "Lembretes:\n"
        for i, lembrete in enumerate(lembretes, start=1):
            resposta += f"{i}. {lembrete['mensagem']} - {lembrete['data_hora'].strftime('%Y-%m-%d %H:%M:%S')}\n"
        enviar_mensagem(resposta, mensagem.chat.id)
    else:
        enviar_mensagem("Nenhum lembrete encontrado.", mensagem.chat.id)

@bot.message_handler(commands=['remover_lembrete'])
def remover_lembrete(mensagem):
    """Remove um lembrete da lista."""
    try:
        numero = int(mensagem.text[len('/remover_lembrete '):])
        if 1 <= numero <= len(lembretes):
            lembretes.pop(numero - 1)
            enviar_mensagem("Lembrete removido com sucesso.", mensagem.chat.id)
        else:
            enviar_mensagem("Número de lembrete inválido.", mensagem.chat.id)
    except Exception as e:
        enviar_mensagem(f"Erro ao remover lembrete: {e}", mensagem.chat.id)

def verificar_lembretes():
    """Verifica e envia lembretes no horário programado."""
    while True:
        agora = datetime.now(pytz.timezone('America/Sao_Paulo'))
        for lembrete in lembretes:
            if lembrete["data_hora"] <= agora:
                enviar_mensagem(f"Lembrete: {lembrete['mensagem']}", lembrete["chat_id"])
                lembretes.remove(lembrete)
        time.sleep(60)

# Conectar ao broker MQTT e iniciar o cliente
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker_address, port, 60)
client.loop_start()

# Iniciar a verificação de lembretes em uma thread separada
threading.Thread(target=verificar_lembretes, daemon=True).start()

# Iniciar o bot do Telegram
bot.polling()
