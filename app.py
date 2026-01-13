import os
import asyncio
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_TOKEN")
SYMBOL = "TONUSDT"
ALERT_DROP = 3.0
CHECK_INTERVAL = 60

if not TOKEN:
    raise Exception("TELEGRAM_TOKEN não definido")

top_price = None
last_price = None
last_alert_level = 0
CHAT_ID = None

# ===== PREÇO =====
def get_price():
    url = "https://api.binance.com/api/v3/ticker/price"
    r = requests.get(url, params={"symbol": SYMBOL}, timeout=10)
    return float(r.json()["price"])

# ===== COMANDOS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CHAT_ID
    CHAT_ID = update.effective_chat.id
    await update.message.reply_text("🤖 Bot conectado. Monitorando TONUSDT.")

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price = get_price()
    await update.message.reply_text(f"💰 TONUSDT: {price}")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global top_price, last_price

    if not top_price:
        await update.message.reply_text("Ainda coletando dados…")
        return

    drop = (top_price - last_price) / top_price * 100

    await update.message.reply_text(
        f"📊 TONUSDT\nTopo: {top_price}\nPreço: {last_price}\nQueda: {drop:.2f}%"
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global top_price, last_alert_level
    top_price = None
    last_alert_level = 0
    await update.message.reply_text("🔄 Topo resetado.")

# ===== LOOP =====
async def monitor(app):
    global top_price, last_price, last_alert_level

    while True:
        try:
            price = get_price()
            last_price = price

            if top_price is None or price > top_price:
                top_price = price
                last_alert_level = 0

            drop = (top_price - price) / top_price * 100
            level = int(drop // ALERT_DROP)

            if level > last_alert_level and CHAT_ID:
                last_alert_level = level
                await app.bot.send_message(
                    chat_id=CHAT_ID,
                    text=f"🚨 TONUSDT caiu {drop:.2f}% desde o topo!\nTopo: {top_price}\nPreço: {price}"
                )

        except Exception as e:
            print("Erro:", e)

        await asyncio.sleep(CHECK_INTERVAL)

# ===== START =====
async def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("reset", reset))

    app.create_task(monitor(app))
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())