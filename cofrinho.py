# -*- coding: utf-8 -*-
import logging
import json
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)

# Token do bot via variável de ambiente
TOKEN = os.environ.get('COFRINHO_BOT_TOKEN')
if not TOKEN:
    raise ValueError("COFRINHO_BOT_TOKEN não encontrado nas variáveis de ambiente!")

# Arquivo para armazenar os dados
ARQUIVO_DADOS = "dados_cofrinhos.json"

# Dicionário para armazenar os valores dos potes
potes = {
    'pote1': 0.0,
    'pote2': 0.0,
    'pote3': 0.0
}

def carregar_dados():
    global potes
    try:
        if os.path.exists(ARQUIVO_DADOS):
            with open(ARQUIVO_DADOS, 'r') as arquivo:
                potes = json.load(arquivo)
            logging.info("Dados carregados com sucesso")
    except Exception as e:
        logging.error(f"Erro ao carregar dados: {e}")

def salvar_dados():
    try:
        with open(ARQUIVO_DADOS, 'w') as arquivo:
            json.dump(potes, arquivo)
        logging.info("Dados salvos com sucesso")
    except Exception as e:
        logging.error(f"Erro ao salvar dados: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    mensagem = (
        "Bem-vindo ao Bot de Cofrinhos! 🐷\n\n"
        "Comandos disponíveis:\n"
        "/add_pote1 [valor] - Adiciona valor ao Pote 1\n"
        "/add_pote2 [valor] - Adiciona valor ao Pote 2\n"
        "/add_pote3 [valor] - Adiciona valor ao Pote 3\n"
        "/edit_pote1 [valor] - Edita o valor total do Pote 1\n"
        "/edit_pote2 [valor] - Edita o valor total do Pote 2\n"
        "/edit_pote3 [valor] - Edita o valor total do Pote 3\n"
        "/ver_potes - Mostra o valor de cada pote e o total"
    )
    await update.message.reply_text(mensagem)

async def add_pote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        comando = update.message.text.split()[0]
        pote = comando.split('_')[1]
        
        if not context.args:
            await update.message.reply_text(f"❌ Por favor, informe um valor para o {pote}!")
            return
        
        valor = float(context.args[0].replace(',', '.'))
        potes[pote] += valor
        salvar_dados()
        await update.message.reply_text(f"✅ R$ {valor:.2f} adicionado ao {pote}!\nTotal: R$ {potes[pote]:.2f}")
    
    except (IndexError, ValueError):
        await update.message.reply_text("❌ Valor inválido! Use o formato: /add_pote1 50.00")

async def edit_pote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        comando = update.message.text.split()[0]
        pote = comando.split('_')[1]
        
        if not context.args:
            await update.message.reply_text(f"❌ Por favor, informe um valor para o {pote}!")
            return
        
        valor_antigo = potes[pote]
        valor_novo = float(context.args[0].replace(',', '.'))
        potes[pote] = valor_novo
        salvar_dados()
        await update.message.reply_text(f"✅ Valor do {pote} alterado de R$ {valor_antigo:.2f} para R$ {valor_novo:.2f}")
    
    except (IndexError, ValueError):
        await update.message.reply_text("❌ Valor inválido! Use o formato: /edit_pote1 50.00")

async def ver_potes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    total = sum(potes.values())
    mensagem = (
        "📊 Valores dos Cofrinhos:\n"
        f"• Pote 1: R$ {potes['pote1']:.2f}\n"
        f"• Pote 2: R$ {potes['pote2']:.2f}\n"
        f"• Pote 3: R$ {potes['pote3']:.2f}\n"
        f"💵 Total: R$ {total:.2f}"
    )
    await update.message.reply_text(mensagem)

def main() -> None:
    carregar_dados()
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add_pote1", add_pote))
    application.add_handler(CommandHandler("add_pote2", add_pote))
    application.add_handler(CommandHandler("add_pote3", add_pote))
    application.add_handler(CommandHandler("edit_pote1", edit_pote))
    application.add_handler(CommandHandler("edit_pote2", edit_pote))
    application.add_handler(CommandHandler("edit_pote3", edit_pote))
    application.add_handler(CommandHandler("ver_potes", ver_potes))
    
    print("🐷 Bot Cofrinho iniciado!")
    application.run_polling()

if __name__ == '__main__':
    main()