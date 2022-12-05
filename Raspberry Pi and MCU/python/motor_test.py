import robot_comms

comms = robot_comms.robot_comms("/dev/ttyS0", 115200)

address = 5

while 1:
    state = input('-----\n1 - Forward | 2 - Reverse | 3 - Coast | 5- current state\nq = quit\nMotor state: ')

    if state == 'q':
        break
    else:
        state = int(state)

    if (state == 1 or state == 2):
        speed = int(input('Motor speed: '))
    else:
        speed = 0

    check = state ^ speed

    comms.send_frame(address, [state, speed, check])


    #end = 126
    print('Sending:\naddress: {}, state: {}, speed: {}'.format(address, state, speed))

    rec_data = comms.receive_frame()

    rec_check = rec_data[0]
    print('Needed check: {}, Received check {}'.format(check, rec_check))

    if state == 5:
        if len(rec_data) > 1:
            rec_state = rec_data[1]
            rec_speed = rec_data[2]
            
            if rec_state == 1:
                rec_state = 'forward'
            elif rec_state == 2:
                rec_state = 'reverse'
            elif rec_state == 3:
                rec_state = 'coast'
            elif rec_state == 4:
                rec_state = 'brake'
        else:
            rec_state = -1
            rec_speed = -1
        
        print('-----\nState: {}, speed: {}'.format(rec_state, rec_speed))

