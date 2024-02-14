import string
import time
from tkinter import *
import tkinter.messagebox
from PIL import Image, ImageTk
import socket, threading, sys, traceback, os

from rtpPacket import RtpPacket
from tcpPacket import TCPpacket

CACHE_FILE_NAME = "cache-"
CACHE_FILE_EXT = ".jpg"

class clientGUI:

    def __init__(self, master, senders, ips, video_name, data):
        self.request_path = []
        self.ips = ips
        self.video_name = video_name
        self.data = data
        self.senders = senders
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW", self.handler)
        self.createWidgets()
        self.addr = ""
        self.port = 0
        self.rtspSeq = 0
        self.request_id = 0
        self.requestSent = -1
        self.teardownAcked = 0
        self.rtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.frameNbr = 0
        self.state = 0
        self.flag = 1


    def move_window(self, event):
        """Método para mover a janela quando o botão do mouse é pressionado e movido."""
        x, y = event.x_root, event.y_root
        self.master.geometry(f"+{x}+{y}")

    
    def createWidgets(self):
        """Build GUI."""
        # Create Play button		
        self.start = Button(self.master, width=20, padx=3, pady=3)
        self.start["text"] = "Play"
        self.start["command"] = self.setupMovie
        self.start.grid(row=1, column=0, padx=2, pady=2)
		
        # Create Pause button			
        self.pause = Button(self.master, width=20, padx=3, pady=3)
        self.pause["text"] = "Pause"
        self.pause["command"] = self.pauseMovie
        self.pause.grid(row=1, column=1, padx=2, pady=2)
		
        # Create Teardown button
        self.teardown = Button(self.master, width=20, padx=3, pady=3)
        self.teardown["text"] = "Quit"
        self.teardown["command"] =  self.exitClient
        self.teardown.grid(row=1, column=2, padx=2, pady=2)
		
        # Create a label to display the movie
        self.label = Label(self.master, height=19)
        self.label.grid(row=0, column=0, columnspan=3, sticky=W+E+N+S, padx=5, pady=5)

    
    def add_stream_data(self, ip, port, request_id):
        self.addr = ip
        self.port = int(port)
        self.request_id = request_id

    
    def setupMovie(self):
        if self.state == 0:
            for nb in self.senders:
                nb.send_video_request(self.ips, self.video_name)

        elif self.state == 1:
            play_again_packet = TCPpacket('PLAY_AGAIN', '', 0)
            play_again_packet.add_epoch(self.request_id)
            for sender in self.senders:
                sender.send_packet(play_again_packet)
        
        self.state = 2


    def exitClient(self):
        """Teardown button handler."""
        if self.state != 0:
            quit_packet = TCPpacket('QUIT', '', time.time())
            quit_packet.add_epoch(self.request_id)
            quit_packet.path = self.request_path
            for sender in self.senders:
                sender.send_packet(quit_packet)

            os.remove(CACHE_FILE_NAME + str(self.request_id) + CACHE_FILE_EXT) # Delete the cache image from video
        
        else:
            
            disconnect_packet = TCPpacket('DC', '', time.time())
            for sender in self.senders:
                sender.send_packet(disconnect_packet)

        self.master.destroy()
        

    def pauseMovie(self):
        if self.state != 1:
            pause_packet = TCPpacket('PAUSE', '', 0)
            pause_packet.add_epoch(self.request_id)
            for sender in self.senders:
                sender.send_packet(pause_packet)


        self.state = 1


    def listenRtp(self):		
        """Listen for RTP packets."""
        self.rtpSocket.bind((self.addr, self.port))
        self.rtpSocket.settimeout(3)

        while self.flag == 1:
            try:
                data = self.rtpSocket.recv(20480)
                if data:
                    rtpPacket = RtpPacket()
                    rtpPacket.decode(data)

                    currFrameNbr = rtpPacket.seqNum()
                    if self.frameNbr > currFrameNbr:
                        self.frameNbr = 0
										
                    if currFrameNbr > self.frameNbr: # Discard the late packet
                        self.frameNbr = currFrameNbr
                        print("Streaming: " + str(currFrameNbr))

                        
                        self.updateMovie(self.writeFrame(rtpPacket.getPayload()))
            except socket.timeout:
                pass

        self.rtpSocket.close()
        		
	
    def writeFrame(self, data):
        """Write the received frame to a temp image file. Return the image file."""
        cachename = CACHE_FILE_NAME + str(self.request_id) + CACHE_FILE_EXT
        file = open(cachename, "wb")
        file.write(data)
        file.close()
		
        return cachename
	
    def updateMovie(self, imageFile):
        """Update the image file as video frame in the GUI."""
        photo = ImageTk.PhotoImage(Image.open(imageFile))
        self.label.configure(image = photo, height=288) 
        self.label.image = photo
    
    def handler(self):
        """Handler on explicitly closing the GUI window."""
        self.pauseMovie()
        if tkinter.messagebox.askokcancel("Quit?", "Are you sure you want to quit?"):
            self.exitClient()

    
    def self_destroy(self):
        self.flag = 0