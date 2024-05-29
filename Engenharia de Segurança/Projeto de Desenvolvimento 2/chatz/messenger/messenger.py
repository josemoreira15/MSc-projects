from flask import Flask, jsonify, request
import json, jwt

SECRET_KEY = open('security/secret_key.bin', 'rb').read()
app = Flask(__name__)
MEMORY_PATH = 'memory/memory.json'


def load_memory():
    with open(MEMORY_PATH) as memory_file:
        memory = json.load(memory_file)

    return memory


def save_memory(memory):
    with open(MEMORY_PATH, 'w') as memory_file:
        json.dump(memory, memory_file, indent=4)


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


@app.post('/send')
def send():
    data = request.json
    memory = load_memory()
    if data['recipient'] not in memory:
        memory[data['recipient']] = {
            'read': [],
            'unread': []
        }

    nr = len(memory[data['recipient']]['unread']) + len(memory[data['recipient']]['read'])
    memory[data['recipient']]['unread'].append({
        'id': f'M{nr}',
        'sender': data['username'],
        'subject': data['subject'],
        'secret': data['secret']
    })

    save_memory(memory)
    return jsonify({}), 200


@app.get('/inbox')
def inbox():
    data = request.json
    memory = load_memory()

    read = []
    unread = []
    if data['username'] in memory:
        read = [({k: v for k, v in read_msg.items() if k != 'secret'}) for read_msg in memory[data['username']]['read']]
        unread = [({k: v for k, v in unread_msg.items() if k != 'secret'}) for unread_msg in memory[data['username']]['unread']]

    return jsonify({'read': read, 'unread': unread}), 200


@app.get('/inbox/<id>')
def message(id):
    data = request.json
    memory = load_memory()
    message = None

    info = memory[data['username']]
    for read in info['read']:
        if read['id'] == id:
            message = read
            break

    if message == None:
        for unread in info['unread']:
            if unread['id'] == id:
                message = unread
                info['unread'].remove(unread)
                info['read'].append(unread)
                break

    save_memory(memory)

    if message == None:
        return jsonify({}), 500
    
    return jsonify({'message': message}), 200


if __name__ == '__main__':
    app.run(port=23240, debug=True)