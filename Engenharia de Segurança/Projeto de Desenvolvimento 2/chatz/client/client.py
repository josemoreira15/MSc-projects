from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import algorithms, Cipher, modes
from flask import Flask, redirect, render_template, request, url_for
import base64, bcrypt, os, requests

app = Flask(__name__)
GATEWAY_URL = 'http://127.0.0.1:23242'
SECURITY_PATH = 'security'
CLIENT = None
TOKEN = None
PUBLIC_KEYS = None


def save_private_key(username, private_key):
    with open(f'{SECURITY_PATH}/{username}.key', 'w') as private_key_file:
        private_key_file.write(private_key)


def load_private_key(username):
    with open(f'{SECURITY_PATH}/{username}.key') as private_key_file:
        private_key = private_key_file.read()

    return private_key


def build_secret(message, public_key_str):
    public_key = serialization.load_pem_public_key(public_key_str.encode(), backend=default_backend())
    iv = os.urandom(32)
    nonce = os.urandom(12)
    cipher = Cipher(algorithms.AES(iv), modes.GCM(nonce))
    encryptor = cipher.encryptor()
    ciphertext = base64.b64encode(encryptor.update(message.encode()) + encryptor.finalize()).decode()
    tag = base64.b64encode(encryptor.tag).decode()
    encrypted_key = base64.b64encode(public_key.encrypt(iv, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))).decode()
    nn = base64.b64encode(nonce).decode()

    return ciphertext + '.' + encrypted_key + '.' + tag + '.' + nn


def reverse_secret(secret, private_key_str):
    private_key = serialization.load_pem_private_key(private_key_str.encode(), password=None, backend=default_backend())
    ciphertext, encrypted_key, tag, nn = secret.split('.')    
    iv = private_key.decrypt(base64.b64decode(encrypted_key), padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
    cipher = Cipher(algorithms.AES(iv), modes.GCM(base64.b64decode(nn), base64.b64decode(tag)), backend=default_backend())
    decryptor = cipher.decryptor()
    message = decryptor.update(base64.b64decode(ciphertext)) + decryptor.finalize()

    return message.decode()


@app.get('/')
def index():
    global PUBLIC_KEYS
    PUBLIC_KEYS = None
    return render_template('index.html', data=CLIENT)


@app.get('/login')
def login_page(error=''):
    if CLIENT == None:
        return render_template('login.html', data={'error': error})
    
    else:
        return redirect(url_for('index'))


@app.post('/login')
def login():
    response = requests.post(f'{GATEWAY_URL}/login', json={'username': request.form.get('username'), 'password': request.form.get('password')})

    if response.status_code == 200:
        data = response.json()
        global CLIENT, TOKEN
        CLIENT = {
            'username': data.get('username'),
            'company': data.get('company'),
        }
        TOKEN = data.get('token')

        return redirect(url_for('index'))

    else:
        return login_page(error='Invalid credentials!')


@app.get('/signup')
def signup_page(error=''):
    if CLIENT == None:
        return render_template('signup.html', data={'error': error})
    
    else:
        return redirect(url_for('index'))


@app.post('/signup')
def signup():
    global CLIENT, TOKEN

    hashed_password = bcrypt.hashpw(request.form.get('password').encode(), bcrypt.gensalt())
    response = requests.post(f'{GATEWAY_URL}/signup', json={'username': request.form.get('username'), 'password': hashed_password, 'company': request.form.get('company')})

    if response.status_code == 200:
        data = response.json()
        CLIENT = {
            'username': data.get('username'),
            'company': data.get('company'),
        }
        TOKEN = data.get('token')

        save_private_key(data.get('username'), data.get('private_key'))
        return redirect(url_for('index'))

    else:
        return signup_page(error='Choose another username!')


@app.post('/logout')
def logout():
    global CLIENT, TOKEN

    headers = {'Authorization': f'Bearer {TOKEN}'}
    response = requests.post(f'{GATEWAY_URL}/logout', json={'username': CLIENT['username']}, headers=headers)

    if response.status_code == 200:
        CLIENT = None
        TOKEN = None
    
    return redirect(url_for('index'))


@app.get('/metadata')
def metadata_page():
    if CLIENT == None:
        return redirect(url_for('index'))
    
    global PUBLIC_KEYS
    headers = {'Authorization': f'Bearer {TOKEN}'}
    response = requests.get(f'{GATEWAY_URL}/recipients', json={'username': CLIENT['username']}, headers=headers)
    if response.status_code == 200:
        PUBLIC_KEYS = response.json()
        return render_template('metadata.html', data={'client': CLIENT, 'recipients': response.json()})
    
    return redirect(url_for('index'))


@app.post('/metadata')
def metadata():
    subject = request.form.get('subject')
    recipient = request.form.get('recipient')

    return render_template('send.html', data={'client': CLIENT, 'subject': subject, 'recipient': recipient})


@app.post('/send')
def send():
    subject = request.form.get('subject')
    recipient = request.form.get('recipient')
    message = request.form.get('message')

    secret = build_secret(message, PUBLIC_KEYS[recipient])
    headers = {'Authorization': f'Bearer {TOKEN}'}
    requests.post(f'{GATEWAY_URL}/send', json={'username': CLIENT['username'], 'secret': secret, 'subject': subject, 'recipient': recipient}, headers=headers)
    
    return redirect(url_for('index'))


@app.get('/inbox')
def inbox():
    if CLIENT == None:
        return redirect(url_for('index'))
    
    headers = {'Authorization': f'Bearer {TOKEN}'}
    response = requests.get(f'{GATEWAY_URL}/inbox', json={'username': CLIENT['username']}, headers=headers)
    if response.status_code == 200:
        return render_template('inbox.html', data={'client': CLIENT, 'messages': response.json()})
    
    return redirect(url_for('index'))


@app.get('/inbox/<id>')
def message(id):
    if CLIENT == None:
        return redirect(url_for('index'))
    
    headers = {'Authorization': f'Bearer {TOKEN}'}
    response = requests.get(f'{GATEWAY_URL}/inbox/{id}', json={'username': CLIENT['username']}, headers=headers)
    if response.status_code == 200:
        content = response.json()
        message = reverse_secret(content['message']['secret'], load_private_key(CLIENT['username']))

        return render_template('message.html', data={'client': CLIENT, 'message': message, 'sender': content['message']['sender'], 'subject': content['message']['subject']})

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(port=23243, debug=True)