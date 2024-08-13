from functions import create_account
from flask import Flask, jsonify, request
from config import HOST, PORT
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route('/create_account', methods=['POST'])
def create_account_route():
    data = request.json
    full_name = data.get('full_name')
    username = data.get('username')
    password = data.get('password')
    year = data.get('year')
    
    success, result = create_account(full_name=full_name, username=username, password=password, year=year)
    if success:
        return jsonify({'status': 'success', 'data': result}), 201
    else:
        return jsonify({'status': 'error', 'message': result}), 500
    
    
app.run(host=HOST, port=PORT, debug=True)
logger.info(f'Starting Flask application on http://{HOST}:{PORT}')
