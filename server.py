from flask import Flask, request
import requests

app = Flask(__name__)

# 🔑 Токены и настройки
TELEGRAM_BOT_TOKEN = "7788946008:AAGULYh-GIkpr-GA3ZA70ERdCAT6BcGNW-g"
CHAT_ID = "-1002307069728"
TRELLO_API_KEY = "5880197335c3d727693408202c68375d"
TRELLO_TOKEN = "ATTA1ea4c6edf0b2892fec32580ab1417a42f521cd70c11af1453ddd0a4956e72896C175BE4E"
TRELLO_BOARD_ID = "67c19cc6cd0d960e2398be79"

TRELLO_URL = "https://api.trello.com/1"
HEADERS = {"Accept": "application/json"}

# 📌 Функция отправки сообщений в Telegram
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, data=data)

# 📌 Удаление карточки из Trello
@app.route("/delete_card", methods=["DELETE"])
def delete_card():
    data = request.json
    name = data.get("name")

    if not name:
        return "error: Не указано имя карточки", 400  # Текстовый ответ

    # 📌 Получаем список всех карточек на доске
    cards_response = requests.get(f"{TRELLO_URL}/boards/{TRELLO_BOARD_ID}/cards",
                                  params={"key": TRELLO_API_KEY, "token": TRELLO_TOKEN},
                                  headers=HEADERS)

    if cards_response.status_code != 200:
        return "error: Ошибка при получении списка карточек", 500  # Текстовый ответ

    cards = cards_response.json()
    card = next((c for c in cards if c["name"] == f"Заявка от {name}"), None)

    if not card:
        return "error: Карточка не найдена", 404  # Текстовый ответ

    card_id = card["id"]

    # 📌 Удаляем карточку
    delete_response = requests.delete(f"{TRELLO_URL}/cards/{card_id}",
                                      params={"key": TRELLO_API_KEY, "token": TRELLO_TOKEN},
                                      headers=HEADERS)

    if delete_response.status_code == 200:
        send_telegram_message(f"🗑 *Удалена карточка*\n📌 Имя: {name}")
        return f"success: Карточка '{name}' удалена", 200  # Текстовый ответ
    else:
        return "error: Ошибка удаления карточки", 500  # Текстовый ответ

# 📌 Обработчик ошибок (гарантированно возвращает текст)
@app.errorhandler(500)
@app.errorhandler(400)
@app.errorhandler(404)
def handle_error(e):
    return f"error: {str(e)}", e.code  # Всегда возвращает текст

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
