import os
import time
import requests

# ====== CONFIG ======
SYMBOL = "TONUSDT"
INTERVAL = 60  # segundos entre cada verificação
DROP_PERCENT = 3.0  # alerta quando cair 3% do topo
BINANCE_URL = "https://api.binance.com/api/v3/ticker/price"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise Exception("TELEGRAM_TOKEN não definido")

# Coloque seu chat_id aqui depois do primeiro /start
CHAT_ID = None

# ===================

def send_telegram(msg):
    global CHAT_ID
    if not CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def get_price():
    r = requests.get(BINANCE_URL, params={"symbol": SYMBOL})
    return float(r.json()["price"])

def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    params = {"timeout": 100}
    if offset:
        params["offset"] = offset
    return requests.get(url, params=params).json()

print("🚀 Robô TON iniciado")

top_price = 0.0
last_alert_top = 0.0
update_id = None

while True:
    try:
        # ================= Telegram =================
        data = get_updates(update_id)

        for result in data.get("result", []):
            update_id = result["update_id"] + 1
            msg = result.get("message", {})
            text = msg.get("text", "")
            chat = msg.get("chat", {})

            if CHAT_ID is None:
                CHAT_ID = chat["id"]
                send_telegram("🤖 Bot conectado. Monitorando TONUSDT.")

            if text == "/price":
                price = get_price()
                send_telegram(f"📊 TONUSDT: {price}")

            if text == "/top":
                send_telegram(f"🏔️ Topo atual: {top_price}")

        # ================= Preço =================
        price = get_price()

        # Atualiza topo
        if price > top_price:
            top_price = price
            last_alert_top = top_price
            send_telegram(f"📈 Novo topo do dia: {top_price}")

        # Calcula queda
        if top_price > 0:
            drop = (top_price - price) / top_price * 100

            if drop >= DROP_PERCENT:
                if last_alert_top == top_price:
                    send_telegram(
                        f"🔻 TON caiu {drop:.2f}% do topo\nTopo: {top_price}\nPreço atual: {price}"
                    )
                    last_alert_top = 0  # impede spam até novo topo

        time.sleep(INTERVAL)

    except Exception as e:
        print("Erro:", e)
        time.sleep(10)