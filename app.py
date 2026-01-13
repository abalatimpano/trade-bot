import os
import requests
from telegram.ext import Updater, CommandHandler

TOKEN = os.environ.get("TELEGRAM_TOKEN")

if not TOKEN:
    raise Exception("ERRO: variável TELEGRAM_TOKEN não configurada no Render")

def start(update, context):
    update.message.reply_text("🤖 Bot de trade está online!")

def price(update, context):
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=10)
        data = r.json()
        price = data["price"]
        update.message.reply_text(f"💰 BTC/USDT: ${price}")
    except Exception as e:
        update.message.reply_text("Erro ao buscar preço.")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("price", price))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()