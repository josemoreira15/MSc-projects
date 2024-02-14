import socket
import threading
from udpSender import UDPsender
from rtpPacket import RtpPacket

class UDPreceiver:

    def __init__(self, host_ip, host_port): 
        self.host_ip = host_ip
        self.host_port = int(host_port)
        self.rtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.event = threading.Event()
        self.teardownAcked = 0
        self.frameNbr = 0
        self.udpSender = []
        self.flag = 1
        self.rtpSocket.settimeout(2)

    
    def add_udpSender(self, client_ip):
        udpSender = UDPsender(client_ip, self.host_port)
        self.udpSender.append(udpSender)


    def listenRtp(self):		
        """Listen for RTP packets."""
        print(self.host_ip)
        print(self.host_port)
        self.rtpSocket.bind((self.host_ip, self.host_port))
        while self.flag == 1:
            try:
                data = self.rtpSocket.recv(20480)
                if data:
                    rtpPacket = RtpPacket()
                    rtpPacket.decode(data)
					
                    currFrameNbr = rtpPacket.seqNum()
                    if self.frameNbr > currFrameNbr:
                        self.frameNbr = 0
                    print(self.udpSender)
                    print("Current Seq Num: " + str(currFrameNbr))

                    if currFrameNbr > self.frameNbr: # Discard the late packet
                        self.frameNbr = currFrameNbr

                    for sender in self.udpSender:
                        if sender.state == 2:
                            sender.send_packet(data)

                        
            except socket.timeout:
                # Stop listening upon requesting PAUSE or TEARDOWN
                # if self.event.isSet():
                #    break
                pass
                
            
    def shutdown_stream_request(self, ip):
        for sender in self.udpSender:
            if sender.IP == ip:
                sender.shutdown_sender()
                self.udpSender.remove(sender)
                break
        
        if len(self.udpSender) == 0:
            print('estou aqui')
            # self.rtpSocket.close()
            self.flag = 0

    
    def pause_stream(self, ip):
        for sender in self.udpSender:
            if sender.IP == ip:
                sender.state = 1

    
    def play_again_stream(self, ip):
        for sender in self.udpSender:
            if sender.IP == ip:
                sender.state = 2