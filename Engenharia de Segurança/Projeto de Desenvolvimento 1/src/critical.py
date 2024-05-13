from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12
import os, time



class Critical():

    def __init__(self, entity):
        self.entity = entity


    def create_critical_files(self, cert, key):
        if not os.path.exists(f'../certs/{self.entity}'):
            os.makedirs(f'../certs/{self.entity}')

            with open(f'../certs/{self.entity}/{self.entity}.key', 'wb') as key_file:
                key_file.write(key.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.TraditionalOpenSSL, encryption_algorithm=serialization.NoEncryption()))
            with open(f'../certs/{self.entity}/{self.entity}.crt', 'wb') as cert_file:
                cert_file.write(cert.public_bytes(encoding=serialization.Encoding.PEM))
            with open(f'../logs/{self.entity}.txt', 'w') as log_file:
                log_file.write('')


    def get_userdata(self):
        try:
            with open(f'../certs/PKCS12/{self.entity}.p12', "rb") as p12_file:
                p12 = p12_file.read()

        except FileNotFoundError:
            print('MSG SERVICE: user not found... switching to default user (userdata)!')
            self.entity = 'userdata'
            with open(f'../certs/PKCS12/{self.entity}.p12', "rb") as p12_file:
                p12 = p12_file.read()
    
        private_key, user_cert, [ca_cert] = pkcs12.load_key_and_certificates(p12, None)
        self.create_critical_files(user_cert, private_key)
        
        return self.entity, private_key, user_cert, ca_cert
    

    def update_logs(self, log):
        with open(f"../logs/{self.entity}.txt", "a") as log_file:
            log_file.write(f'[{self.entity}] ({str(time.time())}) ' + log + '\n')