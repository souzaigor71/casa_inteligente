# -*- coding: utf-8 -*-
import logging
import requests
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Token do bot via variável de ambiente
TOKEN = os.environ.get('DUCO_BOT_TOKEN')
if not TOKEN:
    raise ValueError("DUCO_BOT_TOKEN não encontrado nas variáveis de ambiente!")

DUCO_USER = "deef"
PI_WALLET = "GAWBQ3C7MBTZ6B6AXWP7EWI6U3IQVCFNTP7O47PF5ZKVLJEAB4XDWTB4"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🪙 Bot Cripto Monitor 🚀\n\n"
        f"🔧 Duinocoin: {DUCO_USER}\n"
        f"🔷 Pi Network: {PI_WALLET}\n\n"
        "Comandos disponíveis:\n"
        "/saldo - Ver saldos\n"
        "/mineracao - Status de mineração"
    )

async def saldo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        response_duco = requests.get(f"https://server.duinocoin.com/users/{DUCO_USER}", timeout=10)
        data_duco = response_duco.json()
        
        if data_duco.get("success"):
            balance_duco = float(data_duco["result"]["balance"]["balance"])
            price_response = requests.get("https://server.duinocoin.com/api.json", timeout=10)
            duco_price = float(price_response.json()["Duco price"])
            
            resposta = (
                f"✅ **Duinocoin**\n"
                f"Carteira: {DUCO_USER}\n"
                f"Saldo: {balance_duco:.2f} DUCO\n"
                f"Valor USD: ${(balance_duco * duco_price):.4f}\n\n"
                f"🔷 **Pi Network**\n"
                f"Carteira: {PI_WALLET}\n"
                f"Saldo: (API não disponível)\n"
                f"Valor USD: (Indisponível)"
            )
            
            await update.message.reply_text(resposta)
        else:
            await update.message.reply_text("❌ Erro ao consultar saldo Duinocoin")
    except Exception as e:
        logger.error(f"Erro em /saldo: {str(e)}")
        await update.message.reply_text("⚠️ Erro interno. Tente novamente mais tarde.")

async def mineracao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        response = requests.get(f"https://server.duinocoin.com/users/{DUCO_USER}", timeout=10)
        data = response.json()
        
        if data.get("success"):
            miners = data["result"].get("miners", [])
            resposta = (
                f"⛏️ **Duinocoin**\n"
                f"Carteira: {DUCO_USER}\n"
                f"Mineradores ativos: {len(miners)}\n\n"
                f"🔷 **Pi Network**\n"
                f"Carteira: {PI_WALLET}\n"
                f"Status: (Dados não disponíveis)"
            )
            await update.message.reply_text(resposta)
        else:
            await update.message.reply_text("❌ Erro ao verificar mineração")
    except Exception as e:
        logger.error(f"Erro em /mineracao: {str(e)}")
        await update.message.reply_text("⚠️ Erro interno. Tente novamente mais tarde.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("saldo", saldo))
    app.add_handler(CommandHandler("mineracao", mineracao))
    
    print("🪙 Bot Duco Monitor iniciado!")
    app.run_polling()

if __name__ == "__main__":
    main()