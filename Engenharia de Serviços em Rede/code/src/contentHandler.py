import os
from random import randint
import socket
from clientGUI import clientGUI
from tcpPacket import TCPpacket
from videoStream import VideoStream
from udpServer import UDPserver
from udpReceiver import UDPreceiver
from tkinter import Tk
from tcpSender import TCPsender
import time



class ContentHandler:

    def __init__(self, client_socket, client_addr, data, ip, senders):
        
        self.client_socket = client_socket
        self.client_addr = client_addr # (ip,port)
        self.data = data
        self.ip = ip
        self.senders = senders
        self.flag = 1

        self.client_socket.settimeout(3)

    def content_reader(self):
        buffer = b''

        while self.flag == 1:

            try:
                byte = self.client_socket.recv(1)
                if byte == b'\n':
                    self.handle_content(buffer)
                    buffer = b''
                else:
                    buffer += byte
            
            except socket.timeout:
                pass

    
    def handle_content(self, byte_content):
        content = byte_content.decode() 

        packet = TCPpacket("", "", 0)
        packet.decode_packet(content)

        if packet.src == '':
            packet.src = self.client_addr[0]

        print(packet)

        if packet.id == 'C':
            self.handle_initial_connection()
        
        elif packet.id == 'RJ':
            self.handle_rejoin_connection()
        
        elif packet.id == 'DC':
            self.handle_disconnection(packet)

        elif packet.id == 'LT':
            self.handle_test_connection(packet)
            
        elif packet.id == 'RT':
            self.handle_response_test_connection(packet)
        
        elif packet.id == 'RS':
            self.handle_video_request(packet)

        elif packet.id == 'ACK1':
            self.handle_streaming_ack1(packet)
        
        elif packet.id == 'ACK2':
            self.handle_streaming_ack2(packet)

        elif packet.id == 'SETUP':
            self.handle_SETUP_request(packet)
        
        elif packet.id == 'PLAY':
            self.handle_PLAY_request(packet)

        elif packet.id == 'PAUSE':
            self.handle_PAUSE_request(packet)

        elif packet.id == 'PLAY_AGAIN':
            self.handle_PLAY_AGAIN_request(packet)

        elif packet.id == 'QUIT':
            self.handle_QUIT_request(packet)

        elif packet.id == 'SON':
            self.handle_stream_on(packet)
        
        elif packet.id == 'SOFF':
            self.handle_stream_off(packet)

        elif packet.id == 'MR':
            self.handle_multicast_request(packet)
        
        elif packet.id == 'MUL':
            self.handle_multicast_response(packet)
        
    
    def handle_initial_connection(self):
        self.data.update_connection_status(self.client_addr[0], 'on')
        self.data.print_info()

    
    def handle_rejoin_connection(self):
        self.data.update_connection_status(self.client_addr[0], 'on')
        self.data.print_info()

        sender = TCPsender(self.client_addr[0], self.data.neighbors[self.client_addr[0]]['port'])
        sender.client.connect((sender.ip, sender.port))
        self.senders.append(sender)

        rejoin_accept = TCPpacket('C', '', time.time())
        sender.send_packet(rejoin_accept)


    def handle_disconnection(self, packet):
        if self.client_addr[0] == packet.src:
            self.data.update_connection_status(self.client_addr[0], 'off')
            self.data.print_info()
            for sender in self.senders:
                if sender.ip == self.client_addr[0]:
                    sender.client.close()
                    self.senders.remove(sender)


    def handle_test_connection(self, packet):
        packet.add_to_path(self.client_addr[0])
        if self.data.function == 'sv':
            packet.id = 'RT'
            packet.src = ''
            self.answer_packet(packet, packet.path[-1])
        
        else:
            self.diffuse_packet(packet)
     

    def handle_response_test_connection(self, packet):
        if self.data.function == 'rp':
            latency = time.time() - packet.timestamp
            self.data.add_path(packet.src, packet.path, latency, int(packet.epoch))

        else:
            response_ip = packet.path[packet.path.index(self.ip) - 1]
            self.answer_packet(packet, response_ip)

    
    def handle_video_request(self, packet):
        packet.add_to_path(self.client_addr[0])
        if self.data.function == 'rp':
            flag = self.data.handle_video_request(packet.src, packet.video_name, packet.path)

            if flag == 1:

                best_path = self.data.get_best_path()
                
                udpReceiver = UDPreceiver(best_path[0], self.data.port_counter)
                request_id = str(randint(100000, 999999))
                self.data.add_stream(packet.video_name, packet.src, udpReceiver, request_id)

                new_packet = TCPpacket('SETUP', "", 0)
                new_packet.flag = request_id
                new_packet.set_video_name(packet.video_name)
                new_packet.epoch = self.data.port_counter

                self.data.port_counter += 1
                new_packet.path = best_path

                request_path = self.data.get_request_path(packet.video_name, packet.src)
                udpReceiver.add_udpSender(request_path[-1])
               
                self.answer_packet(new_packet, new_packet.path[1])

        else:

            if self.data.streams_available(packet.video_name):

                request_path = packet.path

                path, port = self.data.get_best_streaming_path(packet.video_name)

                multicast_request = TCPpacket('MR','',time.time())
                request_id = str(randint(100000, 999999))
                multicast_request.set_video_name(packet.video_name)
                multicast_request.path = path
                multicast_request.add_epoch(request_id)
                multicast_request.set_flag(port)

                self.data.add_multicast_request(request_id, packet.path)

                self.answer_packet(multicast_request, path[-1])



            else:
                self.diffuse_packet(packet)


    def handle_SETUP_request(self, packet):
        if self.data.function == 'sv':

            udpStream = UDPserver(packet.video_name, packet.path[-2], packet.epoch)
            request_id = packet.flag
            self.data.add_stream(packet.video_name, packet.src, udpStream, request_id)

            streamimg_ack = TCPpacket('ACK1', '', time.time())
            streamimg_ack.path = packet.path
            streamimg_ack.set_video_name(packet.video_name)
            streamimg_ack.add_epoch(request_id)

            self.answer_packet(streamimg_ack, packet.path[-2])

        else:

            response_ip = packet.path[packet.path.index(self.ip) + 1]
            self.answer_packet(packet, response_ip)

    
    def handle_PLAY_request(self, packet):

        if self.data.function == 'sv':

            request_id = packet.epoch
            self.data.play_stream(request_id)

        else:
            response_ip = packet.path[packet.path.index(self.ip) + 1]
            self.answer_packet(packet, response_ip)


    def handle_PAUSE_request(self, packet):

        self.data.pause_stream(packet.epoch, packet.src)

    
    def handle_PLAY_AGAIN_request(self, packet):

        self.data.play_again_stream(packet.epoch, packet.src)

    
    def handle_streaming_ack1(self, packet):

        if self.data.function == 'rp':
            
            packet.id = 'PLAY'
            self.data.wait_stream(packet.epoch)

            self.answer_packet(packet, packet.path[1])

            request_src = self.data.get_request_src(packet.epoch)
            request_path = self.data.get_request_path(packet.video_name, request_src)
            sender_port = self.data.get_udpSender_port(packet.epoch)

            ack2 = TCPpacket('ACK2', '', time.time())
            ack2.src = request_src
            ack2.path = request_path
            ack2.add_epoch(packet.epoch)
            ack2.set_video_name(packet.video_name)
            ack2.set_flag(sender_port)

            self.answer_packet(ack2, request_path[-1])

            so = TCPpacket('SON', '', time.time())
            so.set_video_name(packet.video_name)
            self.diffuse_packet(so)
        
        else:
            response_ip = packet.path[packet.path.index(self.ip) - 1]

            udpReceiver = UDPreceiver(self.client_addr[0], self.data.port_counter)   ### CONFIRMA ISTO
            udpReceiver.type = 'unicast'
            udpReceiver.add_udpSender(response_ip)
            
            self.data.add_stream(packet.video_name, packet.src, udpReceiver, packet.epoch)
            self.data.wait_stream(packet.epoch)
            
            self.answer_packet(packet, response_ip)

    
    def handle_streaming_ack2(self, packet):

        if self.data.function != 'cl':
            response_ip = packet.path[packet.path.index(self.ip) - 1]

            udpReceiver = UDPreceiver(self.ip, packet.flag)
            udpReceiver.type = 'multicast'
            udpReceiver.add_udpSender(response_ip)

            self.data.add_stream(packet.video_name, packet.src, udpReceiver, packet.epoch)
            self.data.wait_stream(packet.epoch)

            packet.src = ''
            self.answer_packet(packet, response_ip)

            so = TCPpacket('SON', '', time.time())
            so.set_flag(packet.flag)
            so.set_video_name(packet.video_name)
            self.diffuse_packet(so)
        else:

            self.data.clientGUI.request_path = packet.path
            
            self.data.clientGUI.add_stream_data(self.ip, packet.flag, packet.epoch)
            self.data.clientGUI.listenRtp()


    def handle_stream_on(self, packet):
        packet.add_to_path(self.client_addr[0])

        diff_time = time.time() - packet.timestamp

        if self.data.function == 'o':
            if packet.video_name not in self.data.streams_on:
                self.data.streams_on[packet.video_name] = []
            self.data.streams_on[packet.video_name].append((packet.src, packet.path, diff_time, packet.flag))

        self.diffuse_packet(packet)
    

    def handle_stream_off(self, packet):

        if packet.video_name in self.data.streams_on:
            list = self.data.streams_on[packet.video_name]
            for elem in list:
                if packet.src == elem[0]:
                    list.pop(elem)
        
            if len(list) > 0:
                self.data.streams_on[packet.video_name] = list
            else:
                del self.data.streams_on[packet.video_name]
        
        self.diffuse_packet(packet)


    def handle_QUIT_request(self, packet):
        packet.add_to_path(self.client_addr[0])
        if self.data.function != 'cl':

            request_id = packet.epoch
            
            if self.data.quit_stream(request_id, self.client_addr[0]):

                stream_off = TCPpacket('SOFF', '', time.time())
                stream_off.set_video_name(packet.video_name)

                self.diffuse_packet(stream_off)
            
            self.diffuse_packet(packet)
        
        if self.client_addr[0] == packet.src:
            self.data.update_connection_status(self.client_addr[0], 'off')
            self.data.print_info()

            for sender in self.senders:
                if sender.ip == self.client_addr[0]:
                    sender.client.close()
                    self.senders.remove(sender)


    
    def handle_multicast_request(self, packet):

        stream_port = packet.flag

        if self.ip == packet.path[-1]:
            multicast_response = TCPpacket('MUL', '', time.time())
            multicast_response.set_video_name(packet.video_name)
            multicast_response.path = packet.path
            multicast_response.path.append(self.client_addr[0])
            multicast_response.add_epoch(packet.epoch)
            multicast_response.set_flag(stream_port)
            self.answer_packet(multicast_response, multicast_response.path[-1])

        if self.ip == packet.path[0]:

            if len(packet.path) == 1:
                sender_ip = packet.src
            else:
                sender_ip = packet.path[1]

            udpReceiver = self.data.add_multicast_consumer(packet.video_name, sender_ip)
            self.data.add_stream(packet.video_name, packet.src, udpReceiver, packet.epoch)

        else:
            
            last_ip = packet.path[packet.path.index(self.ip) + 1]
            next_ip = packet.path[packet.path.index(self.ip) - 1]

            udpReceiver = UDPreceiver(self.ip, stream_port)
            udpReceiver.add_udpSender(last_ip)

            self.data.add_stream(packet.video_name, packet.src, udpReceiver, packet.epoch)
            self.data.wait_stream(packet.epoch)
      
            self.answer_packet(packet, next_ip)


    def handle_multicast_response(self, packet):
        
        request_id = packet.epoch

        if request_id in self.data.multicast_requests:
            request_path = self.data.multicast_requests[request_id]
            packet.path += request_path

        if self.ip == packet.path[-1]:

            self.data.clientGUI.request_path = packet.path
            
            self.data.clientGUI.add_stream_data(self.ip, packet.flag, packet.epoch)
            self.data.clientGUI.listenRtp()
        
        else:
            stream_port = packet.flag

            next_ip = packet.path[packet.path.index(self.ip) + 1]

            udpReceiver = UDPreceiver(self.ip, stream_port)
            udpReceiver.add_udpSender(next_ip)

            self.data.add_stream(packet.video_name, packet.src, udpReceiver, request_id)
            self.data.wait_stream(packet.epoch)


            self.answer_packet(packet, next_ip)


    def diffuse_packet(self, packet):
        ips_list = [info[0] for info in self.data.ips]
        packet.add_mips(ips_list)

        for sender in self.senders:
            if sender.ip not in packet.mips and sender.ip != packet.src and self.data.neighbors[sender.ip]['status'] == 'on':
                sender.send_packet(packet)
    

    def answer_packet(self, packet, ip):
        for sender in self.senders:
            if ip == sender.ip and self.data.neighbors[ip]['status'] == 'on':
                sender.send_packet(packet)
                break

    
    def close_cycle(self):
        self.flag = 0