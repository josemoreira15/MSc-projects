from flask import Flask, jsonify, request
import datetime, jwt, requests

app = Flask(__name__)
AUTH_URL = 'http://127.0.0.1:23241'
MESSENGER_URL = 'http://127.0.0.1:23240'
SECRET_KEY = open('security/secret_key.bin', 'rb').read()
token = None
expiration = None


def verify_token(token):
    try:
        jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return True
    
    except jwt.ExpiredSignatureError:
        return False
    
    except jwt.InvalidTokenError:
        return False


def check_token():
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'message': 'Access denied'}), 403
    
    token = auth_header.split(' ')[1]
    if not verify_token(token):
        return jsonify({'message': 'Invalid or expired token'}), 403


def confirm_token():
    global token, expiration
    if token is None or datetime.datetime.now(datetime.timezone.utc) >= expiration:
        expiration = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
        token = jwt.encode({'service': 'gateway', 'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)}, SECRET_KEY, algorithm='HS256')

    return token


@app.post('/login')
def login():
    token = confirm_token()
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(f'{AUTH_URL}/login', json=request.json, headers=headers)

    return jsonify(response.json()), response.status_code


@app.post('/signup')
def signup():
    token = confirm_token()
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(f'{AUTH_URL}/signup', json=request.json, headers=headers)

    return jsonify(response.json()), response.status_code


@app.post('/logout')
def logou():
    data = request.json
    check_token()
    token = confirm_token()
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(f'{AUTH_URL}/logout', json={'username': data['username']}, headers=headers)

    return jsonify(response.json()), response.status_code


@app.get('/recipients')
def recipients():
    data = request.json
    check_token()
    token = confirm_token()
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{AUTH_URL}/recipients', json={'username': data['username']}, headers=headers)

    return jsonify(response.json()), response.status_code


@app.post('/send')
def send():
    check_token()
    token = confirm_token()
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(f'{MESSENGER_URL}/send', json=request.json, headers=headers)

    return jsonify(response.json()), response.status_code


@app.get('/inbox')
def inbox():
    data = request.json
    check_token()
    token = confirm_token()
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{MESSENGER_URL}/inbox', json={'username': data['username']}, headers=headers)

    return jsonify(response.json()), response.status_code


@app.get('/inbox/<id>')
def message(id):
    data = request.json
    check_token()
    token = confirm_token()
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{MESSENGER_URL}/inbox/{id}', json={'username': data['username']}, headers=headers)

    return jsonify(response.json()), response.status_code


if __name__ == '__main__':
    app.run(port=23242, debug=True)