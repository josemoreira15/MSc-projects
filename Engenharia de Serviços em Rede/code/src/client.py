import os
import time
from tkinter import Tk
import sys

from clientGUI import clientGUI

CACHE_FILE_NAME = "cache-"
CACHE_FILE_EXT = ".jpg"

class Client:
	
    def __init__(self, ips, neighbours, data, video_name):
        self.ips = ips
        self.neighbours = neighbours
        self.data = data
        self.video_name = video_name
        os.environ['DISPLAY'] = ':0.0'
		
    
    def video_request(self):
        time.sleep(7)

        root = Tk()
            
        app = clientGUI(root, self.neighbours, self.ips, self.video_name, self.data)
        app.master.title(self.video_name)

        self.data.clientGUI = app

        root.mainloop()


        self.data.shutdown_receivers()
        app.self_destroy()
        # sys.exit()