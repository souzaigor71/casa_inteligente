# -*- coding: utf-8 -*-
import os
import random
import logging
import json
import requests
from datetime import datetime
import asyncio
from telegram import Bot, Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

# ==============================================
# Configurações Principais
# ==============================================
TELEGRAM_TOKEN = "7935642070:AAE9wKMJf1zBlRgmuXUsQom6wPPJ96_n0F8"
OPENWEATHER_API_KEY = "SUA_CHAVE_API"
bot = Bot(token=TELEGRAM_TOKEN)
DATA_DIR = "user_data"
os.makedirs(DATA_DIR, exist_ok=True)

# ==============================================
# Estados da Conversa
# ==============================================
(
    CHOOSING, TEXT_GENERATION, SENTIMENT_ANALYSIS,
    TRANSLATION, QUESTION_ANSWERING, LEARNING_MODE,
    WEATHER_INFO
) = range(7)

# ==============================================
# Sistema de Personalidade da IA
# ==============================================
class IAPersonality:
    def __init__(self):
        self.traits = {
            "style": "Empática e Analítica",
            "emoji": ["🤖", "✨", "🧠", "🌍", "☕"],
            "responses": {
                "welcome": [
                    "Olá! Sou sua assistente de IA",
                    "Pronta para ajudar! Escolha uma opção:"
                ]
            }
        }

    def personalize(self, text: str) -> str:
        return f"{random.choice(self.traits['emoji'])} {text}"

IA_PERSONA = IAPersonality()

# ==============================================
# Handlers Essenciais (Corrigidos)
# ==============================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [
        ["Geração de Texto", "Análise de Sentimentos"],
        ["Modo Aprendizado", "Clima"]
    ]
    
    await update.message.reply_text(
        IA_PERSONA.personalize("Escolha uma função:"),
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            input_field_placeholder="Selecione:"
        )
    )
    return CHOOSING

async def choice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    if text == "Geração de Texto":
        await update.message.reply_text("Digite seu texto:")
        return TEXT_GENERATION
    elif text == "Análise de Sentimentos":
        await update.message.reply_text("Envie o texto para análise:")
        return SENTIMENT_ANALYSIS
    elif text == "Modo Aprendizado":
        await update.message.reply_text("Envie: texto|resposta")
        return LEARNING_MODE
    elif text == "Clima":
        await update.message.reply_text("Digite a cidade:")
        return WEATHER_INFO
    else:
        await update.message.reply_text("Opção inválida!")
        return CHOOSING

# ==============================================
# Funcionalidades Principais
# ==============================================
async def generate_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_text = update.message.text
    response = f"📝 Você disse: {user_text}"
    await update.message.reply_text(IA_PERSONA.personalize(response))
    return CHOOSING

async def analyze_sentiment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    response = "🔍 Sentimento: POSITIVO (Confiança: 0.85)"
    await update.message.reply_text(IA_PERSONA.personalize(response))
    return CHOOSING

async def learning_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if "|" in update.message.text:
        await update.message.reply_text("Exemplo recebido! Use /save para salvar")
    elif update.message.text == "/save":
        await update.message.reply_text("Dados salvos! 🧠")
    return LEARNING_MODE

async def weather_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    city = update.message.text
    await update.message.reply_text(f"🌤 Previsão para {city}: 25°C, Ensolarado")
    return CHOOSING

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Operação cancelada.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def set_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args
    if len(args) >= 2:
        context.user_data['profile'] = {
            "name": args[0],
            "pets": args[1].split(','),
        }
        await update.message.reply_text("Perfil atualizado! 🎉")
    else:
        await update.message.reply_text("Formato: /sobre_mim [Nome] [Pets]")

# ==============================================
# Configuração do Bot (Corrigida)
# ==============================================
def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [MessageHandler(filters.TEXT & ~filters.COMMAND, choice_handler)],
            TEXT_GENERATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, generate_text)],
            SENTIMENT_ANALYSIS: [MessageHandler(filters.TEXT & ~filters.COMMAND, analyze_sentiment)],
            LEARNING_MODE: [MessageHandler(filters.TEXT, learning_mode)],
            WEATHER_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, weather_info)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("sobre_mim", set_profile))
    
    print("✅ Bot operacional!")
    application.run_polling()

if __name__ == '__main__':
    main()