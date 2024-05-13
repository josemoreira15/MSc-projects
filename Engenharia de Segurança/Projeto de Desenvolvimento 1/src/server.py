from critical import Critical
import json, socket, ssl, time



class Server:

    def __init__(self):
        self.memory = {}
        self.host = ('127.0.0.1', 7070)
        self.context = None
        self.bindsocket = None


    def load_memory(self):
        with open('../memory/memory.json') as memory_file:
            self.memory = json.load(memory_file)

    
    def update_memory(self):
        with open('../memory/memory.json', "w") as memory_file:
            json.dump(self.memory, memory_file, indent=4)


    def set_context(self):
        self.context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self.context.verify_mode = ssl.CERT_REQUIRED
        self.context.minimum_version = ssl.TLSVersion.TLSv1_3
        self.context.load_cert_chain(certfile='../certs/SERVER/SERVER.crt', keyfile='../certs/SERVER/SERVER.key')
        self.context.load_verify_locations(cafile='../certs/CA.crt')
    

    def set_socket(self):
        self.bindsocket = socket.socket()
        self.bindsocket.bind(self.host)
        self.bindsocket.listen(5)


    def server_service(self):
        cr = Critical('SERVER')
        _, private_key, server_cert, ca_cert = cr.get_userdata()
        cr.update_logs(f'turning on')
        self.load_memory()
        self.set_context()
        self.set_socket()

        try:
            while True:
                handle_socket, client_addr = self.bindsocket.accept()
                conn = self.context.wrap_socket(handle_socket, server_side=True)
                cr.update_logs(f'connection established with {client_addr}')

                try:
                    while True:
                        data = json.loads(conn.recv(4096).decode())
                        cr.update_logs(f'{data["user"]} sent a "{data["flag"]}" request')

                        if (data['user'] in self.memory):

                            if data['flag'] == 'signup':
                                answer = {'flag': 'signup', 'answer': 'MSG SERVICE: you already signed up!' }
                                conn.send(json.dumps(answer).encode())

                            elif data['flag'] == 'exit':
                                answer = {'flag': 'exit'}
                                conn.send(json.dumps(answer).encode())
                                break

                            elif data['flag'] == 'askqueue':
                                content = {}
                                for message in self.memory[data['user']]['queue']:
                                    if self.memory[data['user']]['queue'][message]['status'] == 'unread':
                                        content[message] = self.memory[data['user']]['queue'][message]

                                answer = { 'flag': 'askqueue', 'answer': content }
                                conn.send(json.dumps(answer).encode())

                            elif data['flag'] == 'getmsg':
                                if data['num'] in self.memory[data['user']]['queue']:
                                    self.memory[data['user']]['queue'][data['num']]['status'] = 'read'
                                    sender = self.memory[data['user']]['queue'][data['num']]['sender']
                                    answer = { 'flag': 'getmsg', 'status': 'OK', 'sender': sender, 'answer': self.memory[data['user']]['queue'][data['num']]['secret'], 'cert': self.memory[sender]['cert']}
                                else:
                                    answer = { 'flag': 'getmsg', 'status': 'ERR', 'answer': 'MSG SERVICE: unknown message!' }
                                
                                conn.send(json.dumps(answer).encode())

                            elif data['flag'] == 'send':
                                if data['status'] == 0:
                                    if data['destination'] in self.memory:
                                        answer = { 'flag': 'send', 'answer': { 'cert': self.memory[data['destination']]['cert'] } }
                                        conn.send(json.dumps(answer).encode())

                                        data = json.loads(conn.recv(4096).decode())
                                        self.memory[data['destination']]['queue'][str(len(self.memory[data['destination']]['queue']))] = { 'sender': data['user'], 'timestamp': str(time.time()), 'subject': data['subject'], 'secret': data['secret'], 'status': 'unread' }

                                    else:
                                        answer = { 'flag': 'send', 'answer': 'MSG SERVICE: unknown user!' }
                                        conn.send(json.dumps(answer).encode())

                        else:
                            if data['flag'] == 'signup':
                                self.memory[data['user']] = { 'cert': data['cert'], 'queue': {} }
                                answer = {'flag': 'signup', 'answer': 'OK'}

                            elif data['flag'] == 'exit':
                                answer = {'flag': 'exit'}
                                conn.send(json.dumps(answer).encode())
                                break

                            else:
                                answer = {'flag': 'signup', 'answer': 'MSG SERVICE: you have to signup!'}
                            
                            conn.send(json.dumps(answer).encode())

                finally:
                    conn.shutdown(socket.SHUT_RDWR)
                    conn.close()
                    cr.update_logs(f'connection closed with {client_addr}')
                    self.update_memory()


        except KeyboardInterrupt:
            cr.update_logs('shutting down')
            self.update_memory()
            self.bindsocket.close()



def main():
    sv = Server()
    sv.server_service()


if __name__ == '__main__':
    main()