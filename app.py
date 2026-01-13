import os
import time
import requests

# ===== CONFIG =====
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # coloque seu chat_id no Render
SYMBOL = "TON-USDT"
DROP_PERCENT = 3.0        # alerta quando cair 3% do topo
CHECK_INTERVAL = 30      # segundos entre verificações

if not TELEGRAM_TOKEN:
    raise Exception("TELEGRAM_TOKEN não definido")
if not TELEGRAM_CHAT_ID:
    raise Exception("TELEGRAM_CHAT_ID não definido")

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# ===== BINGX (preço público) =====
def get_price():
    url = "https://open-api.bingx.com/openApi/swap/v2/quote/price"
    r = requests.get(url, params={"symbol": SYMBOL}, timeout=10).json()
    return float(r["data"]["price"])

# ===== TELEGRAM =====
def send(msg):
    requests.post(f"{BASE_URL}/sendMessage", json={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg
    }, timeout=10)

# ===== ESTADO DO MONITOR =====
top_price = 0.0          # topo móvel (só sobe)
last_alert_level = 0    # quantos blocos de 3% já alertamos a partir do topo

send("🟢 Monitor TON ativo. Vou avisar quando cair 3% abaixo do topo móvel.")

# ===== LOOP =====
while True:
    try:
        price = get_price()

        # Atualiza o topo móvel (só quando faz novo máximo)
        if price > top_price:
            top_price = price
            last_alert_level = 0  # reset dos níveis quando faz novo topo

        # Calcula a queda a partir do topo
        if top_price > 0:
            drop = (top_price - price) / top_price * 100

            # Nível de alerta (cada 3% é um nível: 1=3%, 2=6%, 3=9%...)
            level = int(drop // DROP_PERCENT)

            # Se cruzou um novo nível de queda, avisa
            if level > last_alert_level:
                msg = (
                    f"🔴 TON EM QUEDA\n"
                    f"Topo: {top_price}\n"
                    f"Preço atual: {price}\n"
                    f"Queda acumulada: {drop:.2f}%"
                )
                send(msg)
                last_alert_level = level

        time.sleep(CHECK_INTERVAL)

    except Exception as e:
        print("Erro:", e)
        time.sleep(10)