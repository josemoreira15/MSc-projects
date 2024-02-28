import asyncio
import hmac
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import x448, ed448
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
from pickle import loads


def generate_keys():
    private_key = x448.X448PrivateKey.generate()
    public_key = private_key.public_key()

    return private_key, public_key


def generate_shared(private_key, peer_public_key):
    shared_key = private_key.exchange(peer_public_key)
    derived_key = HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=b'handshake data').derive(shared_key)
    
    return derived_key


def generate_sign_keys():
    private_key = ed448.Ed448PrivateKey.generate()
    public_key = private_key.public_key()

    return private_key, public_key


def sign_this(private_key, message):
    sign = private_key.sign(message)

    return sign


def tpbc (tweak, key, block, iv):
    derived_tweak_key = hmac.digest(key, tweak, 'sha256')
    cipher = Cipher(algorithms.AES(derived_tweak_key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    cipher_block = encryptor.update(block) + encryptor.finalize()

    return cipher_block


def undo_tpbc (tweak, key, block, iv):
    derived_tweak_key = hmac.digest(key, tweak, 'sha256')
    cipher = Cipher(algorithms.AES(derived_tweak_key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    plain_block = decryptor.update(block) + decryptor.finalize()
    
    return plain_block


def apply_undo_tpbc(blocks, init_counter, nounce, key, iv):
    plaintext = b""
    counter = init_counter
    auth = 16 * b"\x00"
    
    for block in blocks:
        tweak = nounce + counter + b"\x00"
        plain_block = undo_tpbc(tweak, key, block, iv)
        plaintext += plain_block

        counter_length = len(counter)
        int_counter = int.from_bytes(counter, 'big') + 1
        counter = int_counter.to_bytes(counter_length, 'big')
                
        auth = bytes(a ^ b for (a,b) in zip(auth, plain_block))

    return plaintext, auth, counter


def unsolve_last(tweak, key, last_len, iv, last_block):
    bytes_last_len = last_len.to_bytes(16, 'big')
    mask = tpbc(tweak, key, bytes_last_len, iv)
    last_cipher = bytes(a ^ b for (a,b) in zip(last_block, mask))
    
    return last_cipher


def decrypt(content, key):
    cipher_blocks = [content['cipher_blocks'][counter : counter + 16] for counter in range(0, len(content['cipher_blocks']), 16)]
    plaintext, auth, counter = apply_undo_tpbc(cipher_blocks[:-1], content['init_counter'], content['nounce'], key, content['iv'])
    last_plain = unsolve_last(content['nounce'] + counter + b"\x00", key, content['last_len'], content['iv'], cipher_blocks[-1])
    
    plaintext += last_plain[:content['last_len']]
    
    auth = bytes(a ^ b for (a,b) in zip(auth, last_plain))

    m_length = len(plaintext).to_bytes(16, 'big')
    tweak = content['nounce'] + m_length + b"\x01"
    tag = tpbc(tweak, key, auth, content['iv'])
    
    tag_status = True
    if tag != content['tag']:
        tag_status = False
        
    return plaintext, tag_status


async def handle_connection(reader, writer):
    peer_cipher_key  = await reader.read(56)
    peer_sign_key = await reader.read(57)
    peer_sign = await reader.read(114)
    print('[receiver] Peer keys received...')

    private_cipher_key, public_cipher_key = generate_keys()
    private_sign_key, public_sign_key = generate_sign_keys()
    
    public_cipher_key_bytes = public_cipher_key.public_bytes(encoding=serialization.Encoding.Raw,format=serialization.PublicFormat.Raw)
    sign_message = sign_this(private_sign_key, public_cipher_key_bytes)

    writer.write(public_cipher_key_bytes)
    writer.write(public_sign_key.public_bytes(encoding=serialization.Encoding.Raw,format=serialization.PublicFormat.Raw))
    writer.write(sign_message)
    await writer.drain()
    print('[receiver] Public keys sent...')

    try:
        peer_sign_new_key = ed448.Ed448PublicKey.from_public_bytes(peer_sign_key)
        
        peer_sign_new_key.verify(peer_sign, peer_cipher_key)
        print("[receiver] Signature validated...")

        shared_key = generate_shared(private_cipher_key, x448.X448PublicKey.from_public_bytes(peer_cipher_key))
        print("[receiver] Shared key created...")

        read_content = await reader.read()
        cipher = loads(read_content)
        print("[receiver] Cipher received...")

        try:
            peer_sign_new_key.verify(cipher['sign'], cipher['content'])
            print("[receiver] Signature validated...")

            content = loads(cipher['content'])
            plaintext, tag_status = decrypt(content, shared_key)

            if tag_status == False:
                print("[receiver] Invalid tag...")

            else:
                print("[receiver] Message received: " + plaintext.decode())

        except InvalidSignature:
            print("[receiver] Couldn't verify the signature!")

    except InvalidSignature:
        print("[receiver] Couldn't verify the signature!")


async def main():
    server = await asyncio.start_server(handle_connection, 'localhost', 8888)
    
    async with server:
        await server.serve_forever()


asyncio.run(main())