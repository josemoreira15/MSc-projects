import csv
from random import randint
import threading


class Data:
    
    def __init__(self, filepath, function):
        
        self.function = function
        self.available_streams = []
        self.ips = []
        self.neighbors = {}
        self.filepath = filepath
        self.mips = {}
        self.paths = {}
        self.epoch = 0
        self.streaming_controller = {}
        self.port_counter = 4500
        self.requests = []
        self.clientGUI = None
        self.viewers_per_stream = {}
        self.streams_on = {}
        self.tcpReceivers = []
        self.multicast_requests = {}
        self.lock = threading.Lock()


        with open(self.filepath, 'r') as config_file:
            reader = list(csv.reader(config_file))

            for row in reader:
               
                self.ips.append((row[0], int(row[1])))

                self.neighbors[row[2]] = {
                    'port': int(row[3]),
                    'capacity': int(row[4]),
                    'status': "off",
                    'latency': 0,
                    'n_hops_stream: ': float('inf')
                }

                self.mips[row[0]] = row[2]
        
        if self.function in ['cl', 'sv']:
            with open('videos/content.csv', 'r') as streams_file:
                reader = list(csv.reader(streams_file))

                for row in reader:
                    self.available_streams.append(row[0])


    def print_info(self):
        for ip, port in self.ips:
            print(f"home: {ip}:{port}")
        
        for key in self.neighbors:
            print(f"{key}:{self.neighbors[key]['port']}-{self.neighbors[key]['capacity']}   ->   {self.neighbors[key]['status']}")
    

    def update_connection_status(self, ip, status):
        self.lock.acquire()

        if ip in self.neighbors:
            self.neighbors[ip]['status'] = status
        
        self.lock.release()

    
    def add_path(self, dest, path, latency, epoch):

        self.lock.acquire()

        path.append(dest)
        new_path = {
            'n_hops': len(path),
            'path': path,
            'latency': latency
        }

        if self.epoch != epoch or dest not in self.paths:
            self.epoch = epoch
            self.paths[dest] = [new_path]
        else:
            self.paths[dest].paths.append(new_path)

        for ip_key in self.paths:
            self.paths[ip_key] = sorted(self.paths[ip_key], key=lambda x: x['latency'])

        self.lock.release()


    def is_streaming(self): #videoname
        return self.streams_nr != 0
 
    

    def get_best_path(self):

        self.lock.acquire()

        min_latency = float('inf')
        res = None

        for ip, values in self.paths.items():
            holder = values[0]['latency']
            if holder < min_latency:
                min_latency = holder
                res = values[0]['path']

        self.lock.release()

        return res
    

    def handle_video_request(self, src, video, path):
        flag = 1

        for _src, _video, _path in self.requests:
            if src == _src and video == _video:
                flag = 0
                break
        
        if flag == 1:
            self.requests.append((src, video, path))
        
        return flag
    

    #INIT = 0
	#READY = 1
	#PLAYING = 2

    def update_streaming_status(self, request_id, status):
        self.streaming_controller[request_id]['state'] = status


    def add_stream(self, filename, src_ip, udpSocket, request_id):
        self.streaming_controller[request_id] = {
            'video': filename, 
            'src' : src_ip,
            'socket': udpSocket
        }


    def get_request_src(self, request_id):
        return self.streaming_controller[request_id]['src']
    
    
    def get_udpSender_port(self, request_id):
        return self.streaming_controller[request_id]['socket'].host_port
    

    def get_request_path(self, video_name, request_src):
        for _src, _video, _path in self.requests:
            if request_src == _src and video_name == _video:
                return _path
        return []


    def play_stream(self, request_id):
        self.update_streaming_status(request_id, 1)
        stream_request = self.streaming_controller[request_id]
        play_thread = threading.Thread(target=stream_request['socket'].sendRtp)
        play_thread.start()

    
    def wait_stream(self, request_id):
        stream_request = self.streaming_controller[request_id]
        wait_thread = threading.Thread(target=stream_request['socket'].listenRtp)
        wait_thread.start()



    def quit_stream(self, request_id, client_addr):
        if request_id in self.streaming_controller:
            
            self.streaming_controller[request_id]['socket'].shutdown_stream_request(client_addr)
            self.streaming_controller[request_id]['socket'].event.set()

            del self.streaming_controller[request_id]

            return True

        else:
            return False
        
    
    def pause_stream(self, request_id, client_addr):
        if request_id in self.streaming_controller:

            self.streaming_controller[request_id]['socket'].pause_stream(client_addr)

    
    def play_again_stream(self, request_id, client_addr):
        if request_id in self.streaming_controller:

            self.streaming_controller[request_id]['socket'].play_again_stream(client_addr)


    def streams_available(self, video_name):
        return video_name in self.streams_on
    

    def get_best_streaming_path(self, video_name):
        paths = self.streams_on[video_name]
        best_path = min(paths, key=lambda x: x[2])
        return best_path[1], best_path[3]
    

    def add_multicast_consumer(self, video_name, client_ip):
    
        for key in self.streaming_controller:
            if self.streaming_controller[key]['video'] == video_name:
                self.streaming_controller[key]['socket'].add_udpSender(client_ip)
                return self.streaming_controller[key]['socket']            

    def add_multicast_request(self, request_id, path):
        self.multicast_requests[request_id] = path
    


    def shutdown_receivers(self):
        for tcpReceiver in self.tcpReceivers:
            tcpReceiver.shutdown_receiver()