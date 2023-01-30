import serial
import time

class robot_comms:
    
    def __init__(self, device, baudrate) -> None:
        self.ser = serial.Serial(device, baudrate)
        self.address = 1
        
        
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
        
    def receive_frame(self, timeout=1000000):
        # Receives data frame, strips address and end bytes, returns data array

        data = []
        start_time = time.time_ns()
        
        address_good = False
        
        while 1:
            if (time.time_ns() - start_time) > timeout:
                print('Timed out. Address byte receieved: ', address_good, ' | Num data bytes received: ', len(data))
                break
            
            if self.ser.in_waiting > 0:
                new_byte = int.from_bytes(self.ser.read(), 'big')
                #print(new_byte)
                if address_good:
                    if new_byte == 126:
                        total_time = time.time_ns() - start_time
                        break # End of frame
                    else:
                        data.append(new_byte) # Add data to array
                else:
                    if (new_byte >> 7) == 1:                    # Check if an address byte
                        if (new_byte & 127) == self.address:    # Check for the correct address
                            address_good = True                 # Address belongs to RPi
                
        if data:
            #print('Total time: ', total_time)
            return data
        else:
            return [-1]
        
