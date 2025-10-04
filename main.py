import time
import requests
import telebot

# === ТВОИ ДАННЫЕ ===
TELEGRAM_TOKEN = "8493716132:AAGXxxknjiBeCg1gUXtMDOnVBHtcB2X9KhE"
CHAT_ID = "695895353"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# === СПИСОК АКЦИЙ НА ФЬЮЧЕРСАХ MEXC ===
SYMBOLS = [
    "ROBINHOOD_USDT",
    "MCDSTOCK_USDT",
    "FIGSTOCK_USDT",
    "GOOGLSTOCK_USDT",
    "MSFTSTOCK_USDT",
    "MSTRSTOCK_USDT",
    "AMZNSTOCK_USDT",
    "AAPLSTOCK_USDT",
    "BABASTOCK_USDT",
    "NFLXSTOCK_USDT",
    "APPSTOCK_USDT",
    "ADBESTOCK_USDT",
    "CRCLSTOCK_USDT",
    "ORCLSTOCK_USDT",
    "NVIDIA_USDT",
    "AVGOSTOCK_USDT",
    "METASTOCK_USDT",
    "AMDSTOCK_USDT",
    "TESLA_USDT",
    "PLTRSTOCK_USDT"
]

# === НАСТРОЙКИ ===
SWING_THRESHOLD = 0.3  # % минимальное движение
WINDOW = 60            # окно в секундах
API_URL = "https://contract.mexc.com/api/v1/contract/ticker"

# Храним историю цен
price_history = {symbol: [] for symbol in SYMBOLS}


def fetch_price(symbol):
    try:
        r = requests.get(API_URL, params={"symbol": symbol})
        data = r.json()
        return float(data["data"]["lastPrice"])
    except Exception as e:
        print(f"Ошибка fetch_price {symbol}: {e}")
        return None


def detect_swings(symbol, prices):
    """ Проверка на минимум 2 качели в пределах минуты """
    if len(prices) < 3:
        return False

    swings = 0
    for i in range(1, len(prices)):
        change = (prices[i] - prices[i - 1]) / prices[i - 1] * 100
        if abs(change) >= SWING_THRESHOLD:
            swings += 1
    return swings >= 4  # туда-сюда хотя бы 2 раза (в обе стороны)


def main():
    bot.send_message(CHAT_ID, "✅ Бот запущен, отслеживаю алгоритмы...")

    while True:
        for symbol in SYMBOLS:
            price = fetch_price(symbol)
            if price is None:
                continue

            # Добавляем цену в историю
            price_history[symbol].append((time.time(), price))
            # Чистим историю старше 1 минуты
            price_history[symbol] = [
                (t, p) for t, p in price_history[symbol] if time.time() - t <= WINDOW
            ]

            # Берем только цены
            prices = [p for _, p in price_history[symbol]]

            # Проверяем качели
            if detect_swings(symbol, prices):
                msg = f"⚠️ ALERT {symbol}: 🚨 Обнаружен алгоритм!"
                print(msg)
                bot.send_message(CHAT_ID, msg)

        time.sleep(5)


if __name__ == "__main__":
    main()
