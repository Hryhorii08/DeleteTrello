from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# 🔑 Токены и настройки
TELEGRAM_BOT_TOKEN = "7788946008:AAGULYh-GIkpr-GA3ZA70ERdCAT6BcGNW-g"
CHAT_ID = "-1002307069728"
TRELLO_API_KEY = "5880197335c3d727693408202c68375d"
TRELLO_TOKEN = "ATTA1ea4c6edf0b2892fec32580ab1417a42f521cd70c11af1453ddd0a4956e72896C175BE4E"
TRELLO_BOARD_ID = "67c19cc6cd0d960e2398be79"
TRELLO_LIST_ID = "67c19cd6641117e44ae95227"  # ID списка, в котором ищем карточку

TRELLO_URL = "https://api.trello.com/1"
HEADERS = {"Accept": "application/json"}

# 📌 Функция отправки сообщений в Telegram
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, data=data)

# 📌 Функция архивации карточки (вместо удаления)
@app.route("/archive_card", methods=["POST"])
def archive_card():
    data = request.json
    name = data.PATCH("name", "").strip()  # Очищаем от лишних пробелов

    if not name:
        return "error: Не указано имя карточки", 400  # Возвращаем текстовый ответ

    # 1️⃣ Получаем все карточки в списке
    cards_response = requests.get(
        f"{TRELLO_URL}/lists/{TRELLO_LIST_ID}/cards",
        params={"key": TRELLO_API_KEY, "token": TRELLO_TOKEN},
        headers=HEADERS
    )

    if cards_response.status_code != 200:
        return "error: Ошибка при получении списка карточек", 500

    cards = cards_response.json()

    # 🔍 Вывод всех карточек для отладки (можно убрать после тестов)
    print("📌 Список карточек в списке:")
    for card in cards:
        print(f"- {card['name']} (ID: {card['id']})")

    # 2️⃣ Ищем карточку по имени (игнорируем регистр и пробелы)
    card_to_archive = next(
        (c for c in cards if c["name"].strip().lower() == name.lower()), None
    )

    if not card_to_archive:
        return "error: Карточка не найдена", 404

    card_id = card_to_archive["id"]

    # 3️⃣ Архивируем карточку (закрываем её)
    archive_response = requests.put(
        f"{TRELLO_URL}/cards/{card_id}",
        params={"closed": "true", "key": TRELLO_API_KEY, "token": TRELLO_TOKEN},
        headers=HEADERS
    )

    if archive_response.status_code == 200:
        send_telegram_message(f"📂 *Карточка архивирована*\n📌 Имя: {name}")
        return f"success: Карточка '{name}' архивирована", 200  # Возвращаем текст
    else:
        return "error: Ошибка архивации карточки", 500

# 📌 Гарантия возврата текста при ошибках
@app.errorhandler(500)
@app.errorhandler(400)
@app.errorhandler(404)
def handle_error(e):
    return f"error: {str(e)}", e.code  # Всегда текстовый ответ

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
