from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from flask import Flask, jsonify, request
import bcrypt, datetime, json, jwt

app = Flask(__name__)
SECRET_KEY = open('security/secret_key.bin', 'rb').read()
USERS_PATH = 'users/users.json'


def generate_token(username):
    payload = {
        'username': username,
        'exp': datetime.datetime.now(datetime.timezone.utc)
    }

    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


def generate_keys():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.TraditionalOpenSSL, encryption_algorithm=serialization.NoEncryption())
    public_pem = public_key.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)

    return private_pem, public_pem


def load_users():
    with open(USERS_PATH) as users_file:
        users = json.load(users_file)

    return users


def save_users(users):
    with open(USERS_PATH, 'w') as users_file:
        json.dump(users, users_file, indent=4)


def verify_token(token):
    try:
        jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return True
    
    except jwt.ExpiredSignatureError:
        return False
    
    except jwt.InvalidTokenError:
        return False


@app.before_request
def check_token():
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'message': 'Access denied'}), 403
    
    token = auth_header.split(' ')[1]
    if not verify_token(token):
        return jsonify({'message': 'Invalid or expired token'}), 403


@app.post('/login')
def login():
    data = request.json
    users = load_users()
    if data['username'] not in users:
        return jsonify({'message': 'Invalid credentials!'}), 400
    
    if users[data['username']]['status'] == 'online':
        return jsonify({'message': 'Already logged in!'}), 400
    
    if not bcrypt.checkpw(data['password'].encode(), users[data['username']]['password'].encode()):
        return jsonify({'message': 'Invalid credentials!'}), 400
    
    token = generate_token(data['username'])
    users[data['username']]['status'] = 'online'
    data = {
        'username': data['username'],
        'company': users[data['username']]['company'],
        'token': token
    }

    save_users(users)
    return jsonify(data), 200


@app.post('/signup')
def signup():
    data = request.json
    users = load_users()
    if data['username'] in users:
        return jsonify({'message': 'Choose another username!'}), 400
    
    private_pem, public_pem = generate_keys()
    token = generate_token(data['username'])
    
    users[data['username']] = {
        'password': data['password'],
        'company': data['company'],
        'public_key': public_pem.decode(),
        'status': 'online'
    }

    data = {
        'username': data['username'],
        'company': data['company'],
        'private_key': private_pem.decode(),
        'token': token
    }

    save_users(users)
    return jsonify(data), 200


@app.post('/logout')
def logout():
    data = request.json
    users = load_users()

    if data['username'] not in users:
        return jsonify({'message': 'Invalid credentials!'}), 400
    
    if users[data['username']]['status'] == 'offline':
        return jsonify({'message': 'Already logged out!'}), 400
    
    users[data['username']]['status'] = 'offline'
    save_users(users)
    return jsonify({'message': 'Success logging out!'}), 200


@app.get('/recipients')
def recipients():
    data = request.json
    users = load_users()
    recipients = {}

    for user in users:
        if user != data['username']:
            recipients[user] = users[user]['public_key']

    return jsonify(recipients), 200


if __name__ == '__main__':
    app.run(port=23241, debug=True)