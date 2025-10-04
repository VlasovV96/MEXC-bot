import requests
import telebot
import time
import schedule

# --- настройки телеграма ---
TELEGRAM_TOKEN = "8493716132:AAGXxxknjiBeCg1gUXtMDOnVBHtcB2X9KhE"
CHAT_ID = "695895353"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# --- список акций для отслеживания ---
SYMBOLS = [
    "ROBINHOOD_USDT", "MCDSTOCK_USDT", "FIGSTOCK_USDT", "GOOGLSTOCK_USDT",
    "MSFTSTOCK_USDT", "MSTRSTOCK_USDT", "AMZNSTOCK_USDT", "AAPLSTOCK_USDT",
    "BABASTOCK_USDT", "NFLXSTOCK_USDT", "APPSTOCK_USDT", "ADBESTOCK_USDT",
    "CRCLSTOCK_USDT", "ORCLSTOCK_USDT", "NVIDIA_USDT", "AVGOSTOCK_USDT",
    "METASTOCK_USDT", "AMDSTOCK_USDT", "TESLA_USDT", "PLTRSTOCK_USDT"
]

# --- API URL ---
API_URL = "https://contract.mexc.com/api/v1/contract/ticker?symbol={}"

# --- хранение цен для расчета качелей ---
price_history = {s: [] for s in SYMBOLS}
SWING_THRESHOLD = 0.003  # 0.3%
WINDOW_SECONDS = 60

# --- функция получения цены ---
def fetch_price(symbol):
    try:
        url = API_URL.format(symbol)
        r = requests.get(url, timeout=5).json()
        return float(r["data"][0]["lastPrice"])
    except Exception as e:
        print(f"Ошибка fetch_price {symbol}: {e}")
        return None

# --- проверка качелей ---
def check_swings():
    for symbol in SYMBOLS:
        price = fetch_price(symbol)
        if not price:
            continue

        now = time.time()
        price_history[symbol].append((now, price))

        # оставляем только последнюю минуту
        price_history[symbol] = [
            (t, p) for t, p in price_history[symbol] if now - t <= WINDOW_SECONDS
        ]

        prices = [p for _, p in price_history[symbol]]
        if len(prices) < 3:
            continue

        min_p, max_p = min(prices), max(prices)
        change = (max_p - min_p) / min_p
        if change >= SWING_THRESHOLD:
            bot.send_message(CHAT_ID, f"⚠️ ALERT {symbol}: качели {change*100:.2f}% за минуту!")

# --- ежедневный тест ---
def daily_ping():
    bot.send_message(CHAT_ID, "✅ Тест: бот работает (ежедневное сообщение)")

# планировщик: каждый день в 19:30 по Сингапуру (это 14:30 по Москве)
schedule.every().day.at("19:30").do(daily_ping)

# --- запуск ---
if __name__ == "__main__":
    bot.send_message(CHAT_ID, "✅ Бот запущен, отслеживаю алгоритмы...")

    while True:
        # проверка качелей
        check_swings()

        # проверка планировщика
        schedule.run_pending()

        time.sleep(5)
