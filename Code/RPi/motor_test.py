import robot_comms
import time

comms = robot_comms.robot_comms("/dev/ttyS0", 115200, 33)

addr1 = 1
addr2 = 2
addr3 = 3
addr4 = 4

def print_response(resp):
    try:
        if resp[2] == 1:
            resp[2] = 'Forward'
        elif resp[2] == 2:
            resp[2] = 'Reverse'
        elif resp[2] == 3:
            resp[2] = 'Coast'
        elif resp[2] == 4:
            resp[2] = 'Brake'
        msg = 'Motor: {} | State: {} | Speed: {}'.format(resp[0], resp[2], resp[3])
        print(msg)
    except IndexError:
        print('Not enough bytes for motor {}'.format(resp[0]))
        print(resp)

while 1:
    comms.flush_input()
    
    state = input('-----\n1 - Forward | 2 - Reverse | 6 Rotate right | 7 rotate left | 3 - Coast | 4 - Brake | 5- current state\nq = quit\nMotor state: ')

    if state == 'q' or state == 'Q':
        break
    else:
        try:
            state = int(state)
        except ValueError:
            continue

    if (state == 1 or state == 2):
        if state == 1:
            dir1 = 1
            dir2 = 2
        else:
            dir1 = 2
            dir2 = 1
        speed = int(input('Motor speed: '))
    elif (state == 6 or state == 7):
        if state == 6:
            dir1 = 1
            dir2 = 1
        else:
            dir1 = 2
            dir2 = 2
        speed = int(input('Motor speed: '))
    elif state == 3:
        dir1 = 3
        dir2 = 3
        speed = 1
    elif state == 4:
        dir1 = 4
        dir2 = 4
        speed = int(input('Brake force: '))
    elif state == 5:
        dir1 = 5
        dir2 = 5
        speed = 1
    else:
        continue
        
    #address = int(input('Address: '))

    check1 = dir1 ^ speed
    check2 = dir2 ^ speed

    #comms.send_frame(address, [state, speed, check])
    
    comms.send_frame(addr1, [dir1, speed, check1])
    time.sleep(0.0005)
    comms.send_frame(addr2, [dir2, speed, check2])
    time.sleep(0.0005)
    comms.send_frame(addr3, [dir1, speed, check1])
    time.sleep(0.0005)
    comms.send_frame(addr4, [dir2, speed, check2])

    resp1 = comms.receive_frame(comms.MOTOR_FRAME)
    resp2 = comms.receive_frame(comms.MOTOR_FRAME)
    resp3 = comms.receive_frame(comms.MOTOR_FRAME)
    resp4 = comms.receive_frame(comms.MOTOR_FRAME)
    
    print_response(resp1)
    print_response(resp2)
    print_response(resp3)
    print_response(resp4)