from flask import Flask, request
import requests

app = Flask(__name__)

# 🔑 Токены и настройки
TELEGRAM_BOT_TOKEN = "7788946008:AAF8mtYczEkg_O_1iVwmieQPhZoHBUpLz2Q"
CHAT_ID = "-1002307069728"
TRELLO_API_KEY = "5880197335c3d727693408202c68375d"
TRELLO_TOKEN = "ATTA1ea4c6edf0b2892fec32580ab1417a42f521cd70c11af1453ddd0a4956e72896C175BE4E"
TRELLO_BOARD_ID = "67c19cc6cd0d960e2398be79"
TRELLO_LIST_ID = "67c19cd6641117e44ae95227"

TRELLO_URL = "https://api.trello.com/1"
HEADERS = {"Accept": "application/json"}

# 📌 Функция отправки сообщений в Telegram
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, data=data)

# 📌 Архивация карточки в Trello
@app.route("/archive_card", methods=["PATCH"])
def archive_card():
    data = request.json
    name = data.get("name")

    if not name:
        return "error: Не указано имя карточки", 400

    # Запрашиваем все карточки в нужном списке
    cards_response = requests.get(f"{TRELLO_URL}/lists/{TRELLO_LIST_ID}/cards",
                                  params={"key": TRELLO_API_KEY, "token": TRELLO_TOKEN}, headers=HEADERS)

    if cards_response.status_code != 200:
        return "error: Ошибка при получении списка карточек", 500

    cards = cards_response.json()
    card = next((c for c in cards if c["name"] == name), None)

    if not card:
        return "error: Карточка не найдена", 404

    card_id = card["id"]

    # Архивируем карточку
    archive_response = requests.put(f"{TRELLO_URL}/cards/{card_id}/closed",
                                    params={"value": "true", "key": TRELLO_API_KEY, "token": TRELLO_TOKEN},
                                    headers=HEADERS)

    if archive_response.status_code == 200:
        send_telegram_message(f"📦 *Карточка архивирована*\n📌 Имя: {name}")
        return f"success: Карточка '{name}' архивирована", 200
    else:
        return "error: Ошибка при архивации карточки", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
