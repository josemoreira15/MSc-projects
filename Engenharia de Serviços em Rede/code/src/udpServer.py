import socket
import sys, traceback, threading, socket
from rtpPacket import RtpPacket
from videoStream import VideoStream

class UDPserver:

    def __init__(self, filename, client_ip, client_port):
        self.video_name = VideoStream(filename)
        self.rtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_ip = client_ip
        self.client_port = client_port
        self.event = threading.Event()

    
    def sendRtp(self):
        """Send RTP packets over UDP."""
        while True:
            self.event.wait(0.05)

            # Stop sending if request is PAUSE or TEARDOWN
            if self.event.isSet():
                break

            data = self.video_name.nextFrame()
            if not data:
                # Reached the end of the video, restart from the beginning
                self.video_name.restart()
                continue

            frameNumber = self.video_name.frameNbr()
            try:
                address = self.client_ip
                port = int(self.client_port)
                packet = self.makeRtp(data, frameNumber)
                self.rtpSocket.sendto(packet, (address, port))
            except:
                print("Connection Error")
                print('-'*60)
                traceback.print_exc(file=sys.stdout)
                print('-'*60)

        print("All done!")

    
    
    def shutdown_stream_request(self, ip):
        self.rtpSocket.close()

    
    def makeRtp(self, payload, frameNbr):
        """RTP-packetize the video data."""
        version = 2
        padding = 0
        extension = 0
        cc = 0
        marker = 0
        pt = 26 # MJPEG type
        seqnum = frameNbr
        ssrc = 0
		
        rtpPacket = RtpPacket()
		
        rtpPacket.encode(version, padding, extension, cc, seqnum, marker, pt, ssrc, payload)
        print("Encoding RTP Packet: " + str(seqnum))
		
        return rtpPacket.getPacket()