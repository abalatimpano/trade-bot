import os
import time
import requests
import threading
from openai import OpenAI

# ===== CONFIG =====
TELEGRAM_TOKEN = os.getenv("8021780180:AAGKzDG-8dEICJEAmztCLtYoMrjZYqGl0yY")
OPENAI_API_KEY = ("6937699546")

client = OpenAI(api_key=OPENAI_API_KEY)

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
last_update_id = 0

# ===== BYBIT PRICE =====
def get_price(symbol):
    url = f"https://api.bybit.com/v5/market/tickers?category=linear&symbol={symbol}"
    r = requests.get(url).json()
    return float(r["result"]["list"][0]["lastPrice"])

# ===== TELEGRAM =====
def send(chat_id, text):
    requests.post(f"{BASE_URL}/sendMessage", json={
        "chat_id": chat_id,
        "text": text
    })

def ask_ai(message):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é um trader profissional especializado em futuros de criptomoedas."},
            {"role": "user", "content": message}
        ]
    )
    return response.choices[0].message.content

# ===== MONITOR =====
watchlist = {}

def monitor():
    while True:
        for chat_id, data in watchlist.items():
            price = get_price(data["symbol"])
            entry = data["entry"]
            liq = data["liq"]

            if price <= liq * 1.05:
                send(chat_id, f"⚠️ {data['symbol']} PERTO DE LIQUIDAÇÃO!\nPreço: {price}\nLiquidação: {liq}")

            if price >= entry * 1.02:
                send(chat_id, f"📈 {data['symbol']} subiu 2%\nPreço: {price}")

        time.sleep(15)

# ===== BOT LOOP =====
def run():
    global last_update_id
    while True:
        r = requests.get(f"{BASE_URL}/getUpdates", params={"offset": last_update_id + 1}).json()

        for u in r["result"]:
            last_update_id = u["update_id"]
            msg = u["message"]
            chat_id = msg["chat"]["id"]
            text = msg.get("text", "")

            if text.startswith("/start"):
                send(chat_id, "🤖 Bot de trade ativado.\nUse /watch para monitorar um trade.")

            elif text.startswith("/watch"):
                try:
                    _, symbol, entry, liq = text.split()
                    watchlist[chat_id] = {
                        "symbol": symbol.upper(),
                        "entry": float(entry),
                        "liq": float(liq)
                    }
                    send(chat_id, f"✅ Monitorando {symbol}\nEntrada: {entry}\nLiquidação: {liq}")
                except:
                    send(chat_id, "Uso: /watch BTCUSDT 68000 62000")

            else:
                ai = ask_ai(f"Estou operando {text}. Analise risco e tendência.")
                send(chat_id, ai)

        time.sleep(2)

# ===== START =====
threading.Thread(target=monitor).start()
run()