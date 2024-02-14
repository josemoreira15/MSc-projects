import socket
import sys 
import threading
from contentHandler import ContentHandler


class TCPreceiver:

    def __init__(self, ip, port, data, senders):
        
        self.ip = ip
        self.port = port
        self.data = data
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.settimeout(3)
        self.senders = senders
        self.handlers = []
        self.flag = 1

    
    def run_socket(self):
        self.server.bind((self.ip, self.port))
        self.server.listen()

        while self.flag == 1:
            try:
                client_socket, addr = self.server.accept()
                print(f"[*] Connection accepted from {addr[0]}:{addr[1]} by Socket {self.ip}")

                content_handler = ContentHandler(client_socket, addr, self.data, self.ip, self.senders)
                self.handlers.append(content_handler)
                client_handler = threading.Thread(target=content_handler.content_reader)
                client_handler.start()
            
            except socket.timeout:
                pass
        
        self.server.close()

    
    def shutdown_receiver(self):
        for handler in self.handlers:
            handler.close_cycle()
        self.flag = 0