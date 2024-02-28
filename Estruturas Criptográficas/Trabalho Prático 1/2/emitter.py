import asyncio
import os
import hmac
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import x448, ed448
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
from pickle import dumps


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


def padding(blocks):
    last_len = len(blocks[-1])
    blocks[-1] += b"\x00" * (16 - last_len)

    return blocks, last_len


def tpbc (tweak, key, block, iv):
    derived_tweak_key = hmac.digest(key, tweak, 'sha256')
    cipher = Cipher(algorithms.AES(derived_tweak_key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    cipher_block = encryptor.update(block) + encryptor.finalize()
    
    return cipher_block


def apply_tpbc(blocks, nounce, key, iv):
    cipher_blocks = b""
    init_counter = os.urandom(7)
    counter = init_counter
    auth = 16 * b"\x00"

    for block in blocks:
        tweak = nounce + counter + b"\x00"
        cipher_block = tpbc(tweak, key, block, iv)
        cipher_blocks += cipher_block

        counter_length = len(counter)
        int_counter = int.from_bytes(counter, 'big') + 1
        counter = int_counter.to_bytes(counter_length, 'big')
                
        auth = bytes(a ^ b for (a,b) in zip(auth, block))

    return cipher_blocks, auth, counter, init_counter


def solve_last(tweak, key, last_len, iv, last_block):
    bytes_last_len = last_len.to_bytes(16, 'big')
    mask = tpbc(tweak, key, bytes_last_len, iv)
    last_cipher = bytes(a ^ b for (a,b) in zip(last_block, mask))
    
    return last_cipher


def encrypt(message, key):
    nounce = os.urandom(8)
    iv = os.urandom(16)

    blocks = [bytes(message[counter : counter + 16], 'utf-8') for counter in range(0, len(message), 16)]
    padded_blocks, last_len = padding(blocks)

    cipher_blocks, auth, counter, init_counter = apply_tpbc(padded_blocks[:-1], nounce, key, iv)
    last_cipher = solve_last(nounce + counter + b"\x00", key, last_len, iv, padded_blocks[-1])
    cipher_blocks += last_cipher

    auth = bytes(a ^ b for (a,b) in zip(auth, padded_blocks[-1]))

    m_length = len(message).to_bytes(16, 'big')
    tweak = nounce + m_length + b"\x01"
    tag = tpbc(tweak, key, auth, iv)

    return {'cipher_blocks': cipher_blocks, 'tag': tag, 'nounce': nounce, 'init_counter': init_counter, 'last_len': last_len, 'iv': iv}


async def main():
    reader, writer = await asyncio.open_connection('localhost', 8888)
    
    private_cipher_key, public_cipher_key = generate_keys()
    private_sign_key, public_sign_key = generate_sign_keys()

    public_cipher_key_bytes = public_cipher_key.public_bytes(encoding=serialization.Encoding.Raw,format=serialization.PublicFormat.Raw)
    sign_message = sign_this(private_sign_key, public_cipher_key_bytes)

    writer.write(public_cipher_key_bytes)
    writer.write(public_sign_key.public_bytes(encoding=serialization.Encoding.Raw,format=serialization.PublicFormat.Raw))
    writer.write(sign_message)
    await writer.drain()
    print('[emitter] Public keys sent...')

    peer_cipher_key  = await reader.read(56)
    peer_sign_key = await reader.read(57)
    peer_sign = await reader.read(114)
    print('[emitter] Peer keys received...')

    try:
        peer_sign_new_key = ed448.Ed448PublicKey.from_public_bytes(peer_sign_key)
        
        peer_sign_new_key.verify(peer_sign, peer_cipher_key)
        print("[emitter] Signature validated...")
        
        shared_key = generate_shared(private_cipher_key, x448.X448PublicKey.from_public_bytes(peer_cipher_key))
        print("[emitter] Shared key created...")

        plaintext = input("[emitter] Type the message: ")
        
        cipher_result = encrypt(plaintext, shared_key)
        print("[emitter] Message encrypted...")

        cipher_result_tosend = dumps(cipher_result)
        sig = sign_this(private_sign_key, cipher_result_tosend)
        
        final = {'sign': sig, 'content': cipher_result_tosend}
        writer.write(dumps(final))
        await writer.drain()
        print("[emitter] Message sent...")
 
    except InvalidSignature:
        print("[emitter] Couldn't verify the signature!")


asyncio.run(main())