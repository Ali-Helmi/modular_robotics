import robot_comms

comms = robot_comms.robot_comms("/dev/ttyS0", 115200)

address = 5
state = int(input('Motor state: '))
speed = int(input('Motor speed: '))
check = state ^ speed

comms.send_frame(address, [state, speed, check])


#end = 126
print('Sending:\naddress: {}, state: {}, speed: {}'.format(address, state, speed))

rec_data = comms.receive_frame()

rec_check = rec_data[0]
print('Needed check: {}, Received check {}'.format(check, rec_check))

if state == 5:
    rec_state = rec_data[1]
    rec_speed = rec_data[2]
    
    print('State: {}, speed: {}'.format(rec_state, rec_speed))

