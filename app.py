import os
import asyncio
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

SYMBOL = "TONUSDT"
INTERVAL = 60  # segundos
DROP_PERCENT = 3.0

top_price = 0
last_alert_top = 0


def get_price():
    url = "https://api.bybit.com/v5/market/tickers?category=linear&symbol=TONUSDT"
    r = requests.get(url, timeout=10).json()
    return float(r["result"]["list"][0]["lastPrice"])


async def send(msg, app):
    await app.bot.send_message(chat_id=CHAT_ID, text=msg)


async def check_price(app):
    global top_price, last_alert_top

    price = get_price()

    if price > top_price:
        top_price = price

    drop = (top_price - price) / top_price * 100 if top_price > 0 else 0

    if drop >= DROP_PERCENT and top_price != last_alert_top:
        await send(
            f"⚠️ TON caiu {drop:.2f}%\nTopo: {top_price}\nPreço atual: {price}",
            app
        )
        last_alert_top = top_price


async def monitor(app):
    await send("🤖 Bot conectado. Monitorando TONUSDT.", app)
    while True:
        try:
            await check_price(app)
        except Exception as e:
            print("Erro:", e)
        await asyncio.sleep(INTERVAL)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot ativo. Monitorando TONUSDT.")


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price = get_price()
    drop = (top_price - price) / top_price * 100 if top_price > 0 else 0

    await update.message.reply_text(
        f"TONUSDT\nPreço: {price}\nTopo: {top_price}\nQueda: {drop:.2f}%"
    )


async def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check))

    asyncio.create_task(monitor(app))
    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())