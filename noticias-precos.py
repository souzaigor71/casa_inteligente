import os
import requests
import xml.etree.ElementTree as ET
import time

TOKEN = '8045438578:AAHUwiRBL4BSKE24bVDQbSB5OyOW3BZ9MLE'

def pegar_chat_id():
    url = f'https://api.telegram.org/bot{TOKEN}/getUpdates'
    resposta = requests.get(url)
    dados = resposta.json()

    if not dados['result']:
        print("Nenhuma mensagem recebida ainda. Mande uma mensagem para seu bot no Telegram!")
        return None

    chat_id = dados['result'][-1]['message']['chat']['id']
    print(f"chat_id encontrado: {chat_id}")
    return chat_id

def pegar_noticias_rss():
    url = 'https://g1.globo.com/rss/g1/tecnologia/'
    resposta = requests.get(url)
    root = ET.fromstring(resposta.content)

    noticias = []
    for item in root.findall('.//item')[:5]:
        titulo = item.find('title').text
        link = item.find('link').text
        descricao = item.find('description').text
        resumo = descricao.strip().split('<')[0] if descricao else ""
        noticias.append(f"• <b>{titulo}</b>\n{resumo}\n<a href=\"{link}\">Leia mais</a>\n")
    return "\n".join(noticias)

def pegar_precos():
    url = 'https://api.coingecko.com/api/v3/simple/price'
    params = {
        'ids': 'bitcoin,ethereum,duinocoin',
        'vs_currencies': 'usd'
    }
    resposta = requests.get(url, params=params)
    dados = resposta.json()

    bitcoin = dados.get('bitcoin', {}).get('usd', 'N/A')
    ethereum = dados.get('ethereum', {}).get('usd', 'N/A')
    duco = dados.get('duinocoin', {}).get('usd', 'N/A')

    texto_precos = (
        f"💰 <b>Preços das Criptomoedas (USD):</b>\n"
        f"Bitcoin: ${bitcoin}\n"
        f"Ethereum: ${ethereum}\n"
        f"DuinoCoin: ${duco}"
    )
    return texto_precos

def enviar_mensagem(chat_id, texto):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    dados = {
        'chat_id': chat_id,
        'text': texto,
        'parse_mode': 'HTML',
        'disable_web_page_preview': False
    }
    resposta = requests.post(url, data=dados)
    if resposta.ok:
        print("Mensagem enviada com sucesso!")
    else:
        print(f"Falha ao enviar mensagem. Código: {resposta.status_code}")

if __name__ == "__main__":
    chat_id = pegar_chat_id()
    if not chat_id:
        exit()

    while True:
        print("Buscando notícias e preços...")
        noticias = pegar_noticias_rss()
        precos = pegar_precos()

        mensagem = (
            "<b>📰 Últimas notícias de tecnologia (pt-BR):</b>\n\n"
            f"{noticias}\n"
            f"{precos}"
        )

        enviar_mensagem(chat_id, mensagem)

        print("Esperando 10 minutos para próxima atualização...\n")
        time.sleep(600)  # espera 10 minutos
