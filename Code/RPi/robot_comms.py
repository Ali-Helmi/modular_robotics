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
        self.MOTOR_FRAME = 4
        self.SENSOR_FRAME = 3
        self.ARM_FRAME = 4
        
        #error types
        self.TIMEOUT = -1
        self.NOT_ENOUGH_BYTES = -2
        self.BAD_FRAME = -3
        
        # MCU UART ERRORS
        self.GENERAL_ERROR = 234
        self.MISSING_EOF = 235
        self.BAD_DATA = 236
        self.MISSING_DATA = 237
        self.COMM_ERROR = 238
        
        self.error_list = [self.GENERAL_ERROR, self.MISSING_EOF, self.BAD_DATA, self.MISSING_DATA, self.COMM_ERROR]
        
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
        
        print(frame)
        
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
            # There is previous data from a previously malformed frame
            if self.previous_data[0] & 127 == self.address:
                new_data = self.ser.read(size=frame_type-len(self.previous_data) + 1)
                frame = self.previous_data[1:] + new_data
                self.previous_data = []  
        elif self.ser.in_waiting > 0:
            new_byte = int.from_bytes(self.ser.read(), 'big')
            if (new_byte >> 7) == 1:
                if (new_byte & 127) == self.address:
                    frame = list(self.ser.read(size=frame_type + 1))
            else:
                #this is not an address byte, dump until an EOF is found
                new_byte = 0
                eof_start = time.time_ns()
                while new_byte != 126:
                    new_byte = int.from_bytes(self.ser.read(), 'big')
                    if (time.time_ns() - eof_start) > timeout:
                        
                        # Not finding an EOF, just give up
                        break    
        
        if len(frame) < frame_type:
            # Not enough bytes received
            print('Bad Size, Frame: ', frame)
            if frame[1] in self.error_list:
                print(self.check_uart_error(frame[1]))
            return [self.NOT_ENOUGH_BYTES]
        elif frame[frame_type] == 126:
            # Last byte is the EOF, this is a whole frame
            return frame[:-1]
        else:
            # Last byte is not EOF, this potentially contains the next frame
            # Search for the previous EOF or next address and add to previous data
            for i in range(frame_type):
                if frame[i] > 127:
                    # this is an address byte
                    print('ummmm')
                    self.previous_data = frame[i:]
                    break
            print("No EOF, Frame: ", frame)
            return frame
        

    def flush_input(self):
        self.ser.reset_input_buffer()
        self.previous_data = []
        
    
    def check_comm_error(self, error_num):
        if error_num == self.TIMEOUT:
            return 'Timeout'
        if error_num == self.NOT_ENOUGH_BYTES:
            return 'Not enough bytes'
        if error_num == self.BAD_FRAME:
            return 'Bad Frame'
        
        
    def check_uart_error(self, error_num):
        if error_num == self.GENERAL_ERROR:
            return 'General Error'
        elif error_num == self.MISSING_EOF:
            return 'Missing EOF'
        elif error_num == self.BAD_DATA:
            return 'Bad data'
        elif error_num == self.MISSING_DATA:
            return 'Missing data'
        elif error_num == self.COMM_ERROR:
            return 'Communications error'
        else:
            'Error type unknown'