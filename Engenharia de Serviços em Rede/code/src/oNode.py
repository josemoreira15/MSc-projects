import sys
import threading
import time
from data import Data
from tcpReceiver import TCPreceiver
from tcpSender import TCPsender
from client import Client


class oNode:

    def main(self):

        data = Data(sys.argv[1], sys.argv[2])
        senders = []
        data.print_info()

        for neighbor in data.neighbors:
            sender = TCPsender(neighbor, data.neighbors[neighbor]['port'])
            senders.append(sender)

        for ip, port in data.ips:
            tcp_socket = TCPreceiver(ip, port, data, senders)
            data.tcpReceivers.append(tcp_socket)
            socket_handler = threading.Thread(target=tcp_socket.run_socket)
            socket_handler.start()

        time.sleep(int(sys.argv[3]))
        for sender in senders:
            ips_list = [info[0] for info in data.ips]
            if sys.argv[-1] == 'rejoin':
                sender.rejoin_connection(ips_list)
            else:
                sender.init_connection(ips_list)


            if data.function == 'rp':
                latency_test = threading.Thread(target=sender.latency_test, args=(ips_list,data))
                latency_test.start()
            
        if data.function == 'cl':
            ips_list = [info[0] for info in data.ips]
            
            client = Client(ips_list, senders, data, sys.argv[4])
            client.video_request()
                

if __name__ == "__main__":
    oNode().main()