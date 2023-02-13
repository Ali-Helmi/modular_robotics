import queue

import random

class Serial:
    # This is a fake serial class for testing the controller program on a computer
    def __init__(self, device, baudrate, timeout=0) -> None:
        self.device = device
        self.baudrate = baudrate
        self.timeout = timeout
        self.data = queue.Queue()
        self.in_waiting = 0
        self.glitch_enabled = False
        
    
    def add(self, datebyte):
        self.data.put(datebyte)
        self.in_waiting += 1
        
    def write(self, frame):
        frame = list(frame)
        
        if frame[1] == 3:
            self.glitch_enabled = False
        else:
            self.glitch_enabled = True
        
        new_frame = [161, frame[0] & 127, frame[3], frame[1], frame[2], frame[-1]]
        
        for thing in new_frame:
            self.in_waiting += 1
            self.data.put(thing)
        
    def read(self, size=1):
        if size <= self.in_waiting:
            looplen = size
        else:
            looplen = self.in_waiting
        
        return_data = []
            
        while looplen > 0:
            glitch = random.random()
            if (self.glitch_enabled) & (glitch > 0.99):
                # Adds in random dropped frames to test error handling of controller
                self.data.get()
                self.in_waiting -= 1
                looplen -= 1         
            else: 
                return_data.append(self.data.get())
                looplen -= 1
                self.in_waiting -= 1

        return return_data
    
    def reset_input_buffer(self):
        while not self.data.empty():
            self.data.get()
            self.in_waiting -= 1
        
        