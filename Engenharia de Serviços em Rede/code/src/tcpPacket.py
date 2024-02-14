class TCPpacket:

    def __init__(self, id, src, timestamp):

        self.id = id
        self.src = src
        self.path = []
        self.timestamp = timestamp
        self.mips = []
        self.epoch = 0
        self.flag = 0
        self.video_name = ""

    def __str__(self):
        return (
            f"PACKET:\n"
            f"  ID: {self.id}\n"
            f"  Source: {self.src}\n"
            f"  Timestamp: {self.timestamp}\n"
            f"  Path: {self.path}\n"
            f"  MIPS: {self.mips}\n"
            f"  Epoch: {self.epoch}\n"
            f"  Flag: {self.flag}\n"
            f"  Video: {self.video_name}\n"
        )

    
    def add_to_path(self, ip):
        self.path.append(ip)


    def encode_packet(self):
        final_str = self.id + ',' + self.src + ',' + str(len(self.path))
        for p in self.path:
            final_str += ',' + p
        final_str += ',' + str(len(self.mips))
        for m in self.mips:
            final_str += ',' + m 
        final_str += ',' + str(self.flag) + ',' + str(self.timestamp) + ',' + str(self.epoch) + ',' + (self.video_name) + '\n'
        return final_str


    def decode_packet(self, string):
        args = string.split(",")
        path = []
        mips = []

        path_count = int(args[2])
        for i in range(path_count):
            path.append(args[i + 3])

        mips_count = int(args[path_count + 3])
        for i in range(mips_count):
            mips.append(args[i + path_count + 4])

        self.id = args[0]
        self.src = args[1]
        self.path = path
        self.flag = args[-4]
        self.timestamp = float(args[-3])
        self.epoch = args[-2]
        self.video_name = args[-1]
        self.mips = mips

    
    def add_mips(self, ips):
        for ip in ips:
            self.mips.append(ip)

    def add_epoch(self, epoch):
        self.epoch = epoch

    def set_flag(self, value):
        self.flag = value

    def set_video_name(self, video_name):
        self.video_name = video_name