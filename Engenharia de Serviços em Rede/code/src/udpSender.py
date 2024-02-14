import socket

class UDPsender:

    def __init__(self, IP, PORT):
        
        self.rtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.IP = IP
        self.PORT = PORT
        self.state = 2


    def send_packet(self, packet):
        self.rtpSocket.sendto(packet, (self.IP, self.PORT))

    
    def shutdown_sender(self):
        self.rtpSocket.close()
