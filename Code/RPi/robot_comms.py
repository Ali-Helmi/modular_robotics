import platform

# Check the platform the script is running on
if platform.system() == 'Windows':
    # Running on windows, this is a test, load the fake serial
    import fake_serial
elif platform.system() == 'Linux':
    # Running on linux, this is on the RPi, load real serial
    import serial




import time

class robot_comms:
    
    def __init__(self, device, baudrate, address) -> None:
        if platform.system() == 'Windows':
            self.ser = fake_serial.Serial(device, baudrate, timeout=0.1)
        elif platform.system() == 'Linux':
            self.ser = serial.Serial(device, baudrate, timeout=0.1)

        
        self.address = address
        
        self.previous_data = []
        #frame types
        self.MOTOR_FRAME = 5
        
        #error types
        self.TIMEOUT = -1
        self.NOT_ENOUGH_BYTES = -2
        self.BAD_FRAME = -3
        
    def send_frame(self, address, data):
        # Takes data frame and address and input, constructs frame to send
        # over UART
        # Types of frames
        # Motor frame - 3 data bytes: state, speed, check
        # Sensor frame
        # Arm frame?
        # This function just sends the bytes, expects caller to
        # properly format data
        
        
        # Construct frame
        frame = [128 + address]
        
        for item in data:
            frame.append(item)
            
        frame.append(126)
        
        # Create frame bytes and send
        frame_bytes = bytearray(frame)
        self.ser.write(frame_bytes)
        
    def receive_frame(self, frame_type, timeout=1000000):
        # Receives data frame, strips address and end bytes, returns data array
        
        
        start_time = time.time_ns()
        frame = []
        
        
        while self.ser.in_waiting == 0:
            # Wait for the serial port to see something
            # Might need a timeout for this
            cur_time = time.time_ns()
            if (cur_time - start_time) > timeout:
                # waited too long
                return [self.TIMEOUT]
            pass
        
        if len(self.previous_data) > 0:
            if self.previous_data[0] & 127 == self.address:
                new_data = self.ser.read(size=frame_type-len(self.previous_data) + 1)
                frame = self.previous_data[1:] + new_data
                self.previous_data = []  
        elif self.ser.in_waiting > 0:
            new_byte = int.from_bytes(self.ser.read(), 'big')
            if (new_byte >> 7) == 1:
                if (new_byte & 127) == self.address:
                    frame = list(self.ser.read(size=frame_type))
            else:
                #this is not an address byte, dump until an EOF is found
                new_byte = 0
                eof_start = time.time_ns()
                while new_byte != 126:
                    new_byte = int.from_bytes(self.ser.read(), 'big')
                    if (time.time_ns() - start_time) > timeout:
                        # Not finding an EOF, just give up
                        break    
        
        if len(frame) < frame_type:
            # Not enough bytes received
            return [self.NOT_ENOUGH_BYTES]
        elif frame[frame_type-1] == 126:
            # Last byte is the EOF, this is a whole frame
            return frame[:-1]
        else:
            # Last byte is not EOF, this potentially contains the next frame
            # Search for the previous EOF or next address and add to previous data
            for i in range(frame_type):
                if frame[i] > 127:
                    # this is an address byte
                    self.previous_data = frame[i:]
                    break
            
            return [self.BAD_FRAME]
        

    def flush_input(self):
        self.ser.reset_input_buffer()
        self.previous_data = []