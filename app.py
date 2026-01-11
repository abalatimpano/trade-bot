import os
import time
import requests
from openai import OpenAI

# ===== CONFIG =====
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
last_update_id = 0

# ===== BYBIT =====
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

# ===== OPENAI =====
def ask_ai(message):
    r = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é um trader profissional especializado em futuros de criptomoedas."},
            {"role": "user", "content": message}
        ]
    )
    return r.choices[0].message.content

# ===== LOOP =====
while True:
    try:
        r = requests.get(f"{BASE_URL}/getUpdates?offset={last_update_id + 1}").json()

        if "result" in r:
            for u in r["result"]:
                last_update_id = u["update_id"]

                if "message" in u:
                    chat_id = u["message"]["chat"]["id"]
                    text = u["message"].get("text", "")

                    if text.startswith("/price"):
                        symbol = text.split(" ")[1].upper()
                        price = get_price(symbol)
                        send(chat_id, f"{symbol} = {price}")

                    else:
                        reply = ask_ai(text)
                        send(chat_id, reply)

        time.sleep(2)

    except Exception as e:
        print("Erro:", e)
        time.sleep(5)