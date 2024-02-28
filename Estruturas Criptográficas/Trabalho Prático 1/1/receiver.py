import asyncio
import ascon


async def receive_message(reader, _):
    data = await reader.read()
    
    ciphertext = data[:-16]
    mac = data[-16:]

    mac_seed = input("[receiver] Type a seed to generate the mac: ")
    mac_key = ascon.hash(mac_seed.encode(), variant='Ascon-Xof', hashlength=16)

    r_mac = ascon.mac(mac_key, ciphertext, variant="Ascon-Mac", taglength=16)
    if mac != r_mac:
        print('[receiver] Error in authentication!')

    else:
        try:
            key_seed = input("[receiver] Type a seed to generate the cipher key: ")
            nounce_seed = input("[receiver] Type a seed to generate the nounce: ")

            key = ascon.hash(key_seed.encode(), variant='Ascon-Xof', hashlength=16)
            nounce = ascon.hash(nounce_seed.encode(), variant='Ascon-Xof', hashlength=16)

            plaintext = ascon.decrypt(key, nounce, 'ec2324'.encode(), ciphertext, variant="Ascon-128").decode()

            print("[receiver] Message received: " + plaintext)
    
        except Exception:
            print("[receiver] Error in decryption!")


async def main():
    server = await asyncio.start_server(receive_message, 'localhost', 8888)
    
    async with server:
        await server.serve_forever()


asyncio.run(main())