from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# 🔑 API-ключи Trello
TRELLO_API_KEY = "5880197335c3d727693408202c68375d"
TRELLO_TOKEN = "ATTA1ea4c6edf0b2892fec32580ab1417a42f521cd70c11af1453ddd0a4956e72896C175BE4E"

# 📌 ID доски и списка в Trello
TRELLO_BOARD_ID = "67c19cc6cd0d960e2398be79"
TRELLO_LIST_ID = "67c19cd6641117e44ae95227"  # 🔥 Теперь ищем только в этом списке!

TRELLO_URL = "https://api.trello.com/1"
HEADERS = {"Accept": "application/json"}

# 📌 Функция удаления карточки
@app.route("/delete_trello", methods=["POST"])
def delete_trello():
    data = request.json
    name = data.get("name")

    if not name:
        return jsonify({"error": "Имя не указано"}), 400

    # Запрашиваем карточки только из указанного списка
    response = requests.get(f"{TRELLO_URL}/lists/{TRELLO_LIST_ID}/cards",
                            params={"key": TRELLO_API_KEY, "token": TRELLO_TOKEN},
                            headers=HEADERS)

    if response.status_code != 200:
        return jsonify({"error": "Ошибка получения списка карточек"}), 500

    cards = response.json()

    # 🔹 Проверяем, какие карточки есть в списке (для отладки)
    print("🔍 Карточки в списке:", [card["name"] for card in cards])

    # 🔹 Ищем карточку по имени
    card = next((c for c in cards if c["name"] == f"Заявка от {name}"), None)

    if not card:
        return jsonify({"error": "Карточка не найдена"}), 404

    card_id = card["id"]

    # 🔥 Удаляем карточку
    delete_response = requests.delete(f"{TRELLO_URL}/cards/{card_id}",
                                      params={"key": TRELLO_API_KEY, "token": TRELLO_TOKEN},
                                      headers=HEADERS)

    if delete_response.status_code == 200:
        return jsonify({"success": f"Карточка '{name}' удалена"}), 200
    else:
        return jsonify({"error": "Ошибка удаления карточки"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
