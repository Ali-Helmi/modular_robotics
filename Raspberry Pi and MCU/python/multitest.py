import robot_comms

comms = robot_comms.robot_comms("/dev/ttyS0", 115200)

print("q to quit\n")

state = input('Address to toggle: ')

while state != 'q':
    state = int(state)
    
    comms.send_frame(state, [1])
    print(comms.receive_frame()[0])
    
    state = input('Address to toggle: ')