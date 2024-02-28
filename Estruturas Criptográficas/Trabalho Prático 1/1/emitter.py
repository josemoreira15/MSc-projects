import asyncio
import ascon


async def send_message():
    plaintext = input("[emitter] Type the message: ")

    key_seed = input("[emitter] Type a seed to generate the cipher key: ")
    mac_seed = input("[emitter] Type a seed to generate the mac: ")
    nounce_seed = input("[emitter] Type a seed to generate the nounce: ")

    key = ascon.hash(key_seed.encode(), variant='Ascon-Xof', hashlength=16)
    mac_key = ascon.hash(mac_seed.encode(), variant='Ascon-Xof', hashlength=16)
    nounce = ascon.hash(nounce_seed.encode(), variant='Ascon-Xof', hashlength=16)

    ciphertext = ascon.encrypt(key, nounce, 'ec2324'.encode(), plaintext.encode(), variant="Ascon-128")
    mac = ascon.mac(mac_key, ciphertext, variant="Ascon-Mac", taglength=16)

    return ciphertext + mac


async def main():
    _, writer = await asyncio.open_connection('localhost', 8888)

    data = await send_message()

    writer.write(data)
    await writer.drain()

    writer.close()
    await writer.wait_closed()


asyncio.run(main())