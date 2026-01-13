import os
import time
import requests
from telegram import Bot
from telegram.ext import Application, CommandHandler

# ===== CONFIG =====
TOKEN = os.getenv("TELEGRAM_TOKEN")
SYMBOL = "TONUSDT"
ALERT_DROP = 3.0  # %
CHECK_INTERVAL = 60  # segundos

if not TOKEN:
    raise Exception("TELEGRAM_TOKEN não definido")

bot = Bot(token=TOKEN)

# ===== ESTADO GLOBAL =====
top_price = None
last_price = None
last_alerted_level = None

# ===== FUNÇÃO PREÇO =====
def get_price():
    url = "https://api.binance.com/api/v3/ticker/price"
    r = requests.get(url, params={"symbol": SYMBOL}, timeout=10)
    data = r.json()
    return float(data["price"])

# ===== COMANDOS =====
async def start(update, context):
    await update.message.reply_text("🤖 Bot online. Monitorando TONUSDT.")

async def price(update, context):
    price = get_price()
    await update.message.reply_text(f"💰 TONUSDT agora: {price}")

async def status(update, context):
    global top_price, last_price
    if top_price is None:
        await update.message.reply_text("Ainda não tenho dados.")
        return

    drop = (top_price - last_price) / top_price * 100

    msg = (
        f"📊 STATUS TONUSDT\n"
        f"Topo: {top_price}\n"
        f"Preço: {last_price}\n"
        f"Queda: {drop:.2f}%"
    )
    await update.message.reply_text(msg)

async def check(update, context):
    await status(update, context)

async def reset(update, context):
    global top_price, last_alerted_level
    top_price = None
    last_alerted_level = None
    await update.message.reply_text("🔄 Topo resetado. Novo ciclo iniciado.")

# ===== LOOP DE MONITORAMENTO =====
async def monitor(app):
    global top_price, last_price, last_alerted_level

    while True:
        try:
            price = get_price()
            last_price = price

            if top_price is None or price > top_price:
                top_price = price
                last_alerted_level = None

            drop = (top_price - price) / top_price * 100

            if drop >= ALERT_DROP:
                level = int(drop // ALERT_DROP)

                if last_alerted_level != level:
                    last_alerted_level = level
                    await app.bot.send_message(
                        chat_id=CHAT_ID,
                        text=f"🚨 TONUSDT caiu {drop:.2f}% desde o topo!\nTopo: {top_price}\nPreço atual: {price}"
                    )

        except Exception as e:
            print("Erro:", e)

        await app.bot.sleep(CHECK_INTERVAL)

# ===== START =====
def main():
    global CHAT_ID

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("check", check))
    app.add_handler(CommandHandler("reset", reset))

    print("Bot iniciado")
    app.run_polling()

    CHAT_ID = None

if __name__ == "__main__":
    main()