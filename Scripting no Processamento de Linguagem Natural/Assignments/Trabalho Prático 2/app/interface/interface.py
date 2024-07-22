from flask import Flask, render_template, request, jsonify, url_for
import requests

app = Flask(__name__)

API_URL = 'http://127.0.0.1:23241'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.form['message']

    bot_response = requests.post(f'{API_URL}/chat', json={'message': user_message})
    return jsonify({'response': bot_response.json()['response']})

if __name__ == '__main__':
    app.run(port=23242, debug=True)