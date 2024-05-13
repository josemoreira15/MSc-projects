from critical import Critical
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.x509.oid import NameOID
import base64, json, socket, ssl, sys



def help_message():
        return """[INSTRUCTIONS]
-user <FNAME> -- optional argument that specifies the file with user data being, by default, userdata

signup -- regists the user, allowing the server to access his certificate (the user must always start by registering to use the other functionalities of the service)

send <UID> <SUBJECT> -- sends a message with subject <SUBJECT> to the user with identifier <UID>. The message content will be read from stdin and the size must be limited to 1000 bytes

askqueue -- asks the server to send the list of unread messages from the user's queue. For each message in the queue, a line is returned containing: <NUM>:<SENDER>:<TIME>:<SUBJECT>, where <NUM> is the order number of the message in the queue and <TIME> is a timestamp added by the server which records the time at which the message was received

getmsg <NUM> -- requests the server to send the message from the queue with number <NUM>. If successful, the message will be printed to stdout. Once sent, this message will be marked as read, so it will not be listed in the next askqueue command (but may be requested again by the client)"""


def error(message):
    sys.stderr.write(message + '\n')


def help():
    message = help_message()
    print(message)


def mkpair(x, y):
    len_x = len(x)
    len_x_bytes = len_x.to_bytes(2, 'little')
    return len_x_bytes + x + y


def unpair(xy):
    len_x = int.from_bytes(xy[:2], 'little')
    x = xy[2 : len_x + 2]
    y = xy[len_x + 2:]
    return x, y



class Client:

    def __init__(self, user='userdata'):
        self.user = user
        self.host = ('127.0.0.1', 7070)
        self.hostname = 'Message Service Server'
        self.connection = None


    def set_context(self):
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile='../certs/CA.crt')
        context.options = ssl.CERT_REQUIRED
        context.minimum_version = ssl.TLSVersion.TLSv1_3
        context.load_cert_chain(certfile=f'../certs/{self.user}/{self.user}.crt', keyfile=f'../certs/{self.user}/{self.user}.key')

        return context
    

    def set_connection(self):
        context = self.set_context()

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn = context.wrap_socket(sock, server_side=False, server_hostname=self.hostname)
        self.conn.connect(self.host)
    

    def get_message(self):
        while True:
            message = input("[message]: ")
            if len(message.encode()) > 1000:
                error("MSG SERVICE: byte limit error!")
            
            else:
                return message
            
    
    def extract_pseudonym(self, cert):
        pseudonym = None
        for attr in cert.subject:
            if attr.oid == NameOID.PSEUDONYM:
                pseudonym = attr.value
                break

        return pseudonym
            

    def build_secret(self, destination_cert, private_key):
        destination_public_key = destination_cert.public_key()
        message = self.get_message()
        ciphertext = destination_public_key.encrypt(message.encode(), padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
        signature = private_key.sign(ciphertext, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())

        return mkpair(ciphertext, signature)
            
    
    def show_message(self, sender, secret, cert, private_key):
        ciphertext, signature = unpair(base64.b64decode(secret))
        sender_cert = x509.load_pem_x509_certificate(base64.b64decode(cert))
        sender_public_key = sender_cert.public_key()

        try: 
            sender_public_key.verify(signature, ciphertext, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
            pseudonym = self.extract_pseudonym(sender_cert)

            if pseudonym == sender:

                try:
                    message = private_key.decrypt(ciphertext, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)).decode()
                    print(message)

                except Exception:
                    print("MSG SERVICE: verification error!")

            else:
                print("MSG SERVICE: verification error!")

        except Exception:
            print("MSG SERVICE: verification error!")
            
    
    def handle_answer(self, server_answer, private_key, destination, subject):
        if server_answer['flag'] == 'signup':
            if server_answer['answer'] != 'OK':
                print(server_answer['answer'])

        elif server_answer['flag'] == 'askqueue':
            queue = server_answer['answer']
            for num in queue:
                print(f'{num}:{queue[num]["sender"]}:{queue[num]["timestamp"]}:{queue[num]["subject"]}')

        elif server_answer['flag'] == 'getmsg':
            if server_answer['status'] == 'OK':
                self.show_message(server_answer['sender'], server_answer['answer'], server_answer['cert'], private_key)
            else:
                print(server_answer['answer'])

        elif server_answer['flag'] == 'send':
            if type(server_answer['answer']) == str:
                print(server_answer['answer'])

            else:
                destination_cert = x509.load_pem_x509_certificate(base64.b64decode(server_answer['answer']['cert']))
                secret = self.build_secret(destination_cert, private_key)

                data = { 'user': self.user, 'flag': 'send', 'status': 1, 'destination': destination, 'subject': subject, 'secret': base64.b64encode(secret).decode() }
                self.conn.send(json.dumps(data).encode())


    def client_service(self):
        cr = Critical(self.user)
        self.user, private_key, user_cert, ca_cert = cr.get_userdata()
        self.set_connection()
        cr.update_logs(f'connection established with the SERVER')
        
        server_answer = ''
        flag = ''

        while (flag != 'exit'):
            command = input('[command]: ')
            destination = None
            subject = None

            if command == 'signup':
                data = { 'user': self.user, 'flag': 'signup', 'cert': base64.b64encode(user_cert.public_bytes(encoding=serialization.Encoding.PEM)).decode() }
                self.conn.send(json.dumps(data).encode())
                cr.update_logs(f'sent a "signup" request to the SERVER')

            elif command == 'exit':
                data = { 'user': self.user, 'flag': 'exit' }
                self.conn.send(json.dumps(data).encode())
                cr.update_logs(f'sent a "exit" request to the SERVER')

            elif command == 'askqueue':
                data = { 'user': self.user, 'flag': 'askqueue' }
                self.conn.send(json.dumps(data).encode())
                cr.update_logs(f'sent a "askqueue" request to the SERVER')

            else:
                command_content = command.split()

                if len(command_content) == 2 and command_content[0] == 'getmsg':
                    data = { 'user': self.user, 'flag': 'getmsg', 'num': command_content[1] }
                    self.conn.send(json.dumps(data).encode())
                    cr.update_logs(f'sent a "getmsg" request to the SERVER')

                elif len(command_content) == 3 and command_content[0] == 'send':
                    destination = command_content[1]
                    subject = command_content[2]
                    data = { 'user': self.user, 'flag': 'send', 'status': 0, 'destination': destination }
                    self.conn.send(json.dumps(data).encode())
                    cr.update_logs(f'sent a "send" request to the SERVER')

                else:
                    error('MSG SERVICE: command error!')
                    continue
                    
            server_answer = json.loads(self.conn.recv(4096).decode())
            self.handle_answer(server_answer, private_key, destination, subject)
            flag = server_answer['flag']

        self.conn.close()



def main():
    if (len(sys.argv) == 2 and sys.argv[1] == 'help'):
        help()

    elif len(sys.argv) == 1 or (len(sys.argv) == 3 and sys.argv[1] == '-user'):
        if len(sys.argv) == 1:
            cl = Client()
        else:
            cl = Client(sys.argv[2])
        cl.client_service()

    else:
        error('SERVICE: command error!\n\n' + help_message())


if __name__ == '__main__':
    main()