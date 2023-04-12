import robot_comms
import time

arm_addr = 5
grip_addr = 6

comms = robot_comms.robot_comms("/dev/ttyS0", 115200, 33)

def print_response(resp):
    try:
        msg = 'Arm1: {} | Arm2: {}'.format(resp[1], resp[2])
        print(msg)
        print('Resp: ', resp)
    except IndexError:
        print('Data error {}'.format(comms.check_comm_error(resp[0])))
        print(resp)

while 1:
    comms.flush_input()
    
    print('-----\n s for status, q for quit, 1 - Extend, 2 - Retract, 3 - Open Gripper, 4 - Close Gripper')
    
    state = input('Input: ')

    if state == 'q' or state == 'Q':
        break
    elif state == 's' or state =='S':
        comms.send_frame(arm_addr, [110, 111, 110 ^ 111])
    else:
        try:
            if state == '1':
                comms.send_frame(arm_addr, [65, 20, 65^20])
            elif state == '2':
                comms.send_frame(arm_addr, [30, 40, 30^40])
            elif state == '3':
                comms.send_frame(grip_addr, [45, 30, 45^30])
            elif state == '4':
                comms.send_frame(grip_addr, (80, 30, 80^30))
        except ValueError:
            continue

    time.sleep(0.05)
    resp1 = comms.receive_frame(comms.ARM_FRAME)
    
    
    print_response(resp1)