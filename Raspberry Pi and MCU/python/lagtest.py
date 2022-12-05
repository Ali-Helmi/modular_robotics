import time
import robot_comms

comms = robot_comms.robot_comms("/dev/ttyS0", 115200)

for x in range(6):
    
    state = 1
    
    if state:
        comms.send_frame(5, [1])
        state = 0
        state = comms.receive_frame()[0]
    if state:
        comms.send_frame(7, [1])
        state = 0
        state = comms.receive_frame()[0]
    if state:
        comms.send_frame(9, [1])
        state = 0
        state = comms.receive_frame()[0]
    
    time.sleep(2)