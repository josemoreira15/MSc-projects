import socket
from tcpPacket import TCPpacket
import time


class TCPsender:

    def __init__(self, ip, port):
        
        self.ip = ip
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    def send_packet(self, packet):
        encoded_packet = packet.encode_packet()
        self.client.send(encoded_packet.encode())


    def init_connection(self, ips):
        self.client.connect((self.ip, self.port))
        
        packet = TCPpacket("C", "", time.time())
        packet.add_mips(ips)
        self.send_packet(packet)

    
    def rejoin_connection(self, ips):
        self.client.connect((self.ip, self.port))

        packet = TCPpacket("RJ", "", time.time())
        packet.add_mips(ips)
        self.send_packet(packet)


    def latency_test(self, ips, data):
        time.sleep(5)
        epoch = 0
        while True:
            packet = TCPpacket('LT', "", time.time())
            packet.add_mips(ips)
            packet.add_epoch(epoch)
            self.send_packet(packet)
            epoch += 1
            time.sleep(50)
            print(data.paths)


    def send_video_request(self, ips, video):
        packet = TCPpacket("RS", "", time.time())
        packet.add_mips(ips)
        packet.set_video_name(video)
        self.send_packet(packet)


    def close_socket(self):
        self.client.close()