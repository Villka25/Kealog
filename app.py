import os
import json
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Секретный ключ (лучше задавать через переменную окружения)
VALID_KEY = os.environ.get('API_KEY', 'default_key_change_me')

# Файл для хранения данных (в продакшене лучше использовать базу данных)
DATA_FILE = 'keystrokes.log'

@app.route('/log', methods=['POST'])
def log_keystrokes():
    # Проверка API-ключа (через заголовок X-API-Key)
    api_key = request.headers.get('X-API-Key')
    if api_key != VALID_KEY:
        return jsonify({'error': 'Unauthorized'}), 401

    # Получаем JSON из тела запроса
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data'}), 400

    # Добавляем метаданные сервера
    data['server_time'] = datetime.now().isoformat()
    data['client_ip'] = request.remote_addr

    # Сохраняем в файл (каждая запись с новой строки)
    with open(DATA_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False) + '\n')

    return jsonify({'status': 'ok'}), 200

@app.route('/health', methods=['GET'])
def health():
    return 'OK', 200

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
