import robot_comms
import time

addr = 5

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
    
    print('-----\n s for status, q for quit, integer value (1-99) for arm1, 110 for no change')
    
    state = input('Input: ')

    if state == 'q' or state == 'Q':
        break
    elif state == 's' or state =='S':
        comms.send_frame(addr, [110, 111, 110 ^ 111])
    else:
        try:
            state = int(state)
            if (0 < state < 100) or (state == 110):
                print('Integer value (1-99) for arm2, 111 for no change')
                state2 = int(input('Arm2: '))
                if (0 < state2 < 100) or (state2 == 111):
                    check = state ^ state2
                    comms.send_frame(addr, [state, state2, check])
        except ValueError:
            continue

    time.sleep(0.05)
    resp1 = comms.receive_frame(comms.ARM_FRAME)
    
    
    print_response(resp1)