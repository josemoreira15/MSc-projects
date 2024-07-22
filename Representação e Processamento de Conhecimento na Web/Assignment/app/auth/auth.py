from flask import Flask, jsonify, request
import bcrypt, datetime, json, jwt

app = Flask(__name__)
SECRET_KEY = 'gfootdz_secret'
USERS_PATH = 'users/users.json'


def generate_token(username):
    payload = {
        'username': username,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    }

    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


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


def check_token():
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'message': 'Access denied'}), 403
    
    token = auth_header.split(' ')[1]
    if not verify_token(token):
        return jsonify({'message': 'Invalid or expired token'}), 403


@app.post('/entrar')
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
        'token': token
    }

    save_users(users)
    return jsonify(data), 200


@app.post('/sair')
def logout():
    check_token()
    data = request.json
    users = load_users()

    if data['username'] not in users:
        return jsonify({'message': 'Invalid credentials!'}), 400
    
    if users[data['username']]['status'] == 'offline':
        return jsonify({'message': 'Already logged out!'}), 400
    
    users[data['username']]['status'] = 'offline'
    save_users(users)
    return jsonify({'message': 'Success logging out!'}), 200


if __name__ == '__main__':
    app.run(port=23240, debug=True)