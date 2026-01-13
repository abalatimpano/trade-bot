import os
import time
import requests
from telegram import Bot

# =========================
# CONFIG
# =========================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TELEGRAM_TOKEN:
    raise Exception("TELEGRAM_TOKEN não definido")

bot = Bot(token=TELEGRAM_TOKEN)

# Chat ID autorizado (primeira pessoa que falar com o bot)
AUTHORIZED_CHAT_ID = None

SYMBOL = "TON-USDT"
DROP_PERCENT = 3.0   # alerta a cada 3%
CHECK_INTERVAL = 60  # segundos

current_top = None

# =========================
# BingX price
# =========================
def get_price():
    url = "https://open-api.bingx.com/openApi/swap/v2/quote/price"
    params = {"symbol": SYMBOL}
    r = requests.get(url, params=params, timeout=10).json()
    return float(r["data"]["price"])

# =========================
# Telegram
# =========================
def send(msg):
    if AUTHORIZED_CHAT_ID:
        bot.send_message(chat_id=AUTHORIZED_CHAT_ID, text=msg)

# =========================
# Wait for first user
# =========================
def wait_for_user():
    global AUTHORIZED_CHAT_ID
    last_update = None

    print("Aguardando alguém falar com o bot no Telegram...")

    while AUTHORIZED_CHAT_ID is None:
        updates = bot.get_updates(offset=last_update, timeout=10)

        for u in updates:
            last_update = u.update_id + 1
            if u.message:
                AUTHORIZED_CHAT_ID = u.message.chat.id
                bot.send_message(chat_id=AUTHORIZED_CHAT_ID, text="✅ Bot conectado. Monitorando TONUSDT agora.")
                return

        time.sleep(2)

# =========================
# MAIN
# =========================
wait_for_user()

while True:
    try:
        price = get_price()

        global current_top

        # Define topo inicial
        if current_top is None:
            current_top = price
            send(f"📈 Topo inicial da TON: {price:.4f}")
            time.sleep(CHECK_INTERVAL)
            continue

        # Novo topo
        if price > current_top:
            current_top = price
            send(f"🔼 Novo topo da TON: {price:.4f}")

        # Percentual de queda
        drop = (current_top - price) / current_top * 100

        if drop >= DROP_PERCENT:
            send(
                f"🚨 TON CAIU {drop:.2f}%\n"
                f"Topo: {current_top:.4f}\n"
                f"Preço atual: {price:.4f}"
            )

            # Reseta topo para permitir novas quedas de 3%
            current_top = price

        time.sleep(CHECK_INTERVAL)

    except Exception as e:
        print("Erro:", e)
        time.sleep(10)