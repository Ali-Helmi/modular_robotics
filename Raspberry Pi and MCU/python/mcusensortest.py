import time
import robot_comms

comms = robot_comms.robot_comms("/dev/ttyS0", 115200)

while 1:
    comms.send_frame(5, [1])
    distance = comms.receive_frame()[0]
    msg = '\rDistance: ' + str(distance) + ' inches    '
    print(msg, end='')
    
    time.sleep(0.5)