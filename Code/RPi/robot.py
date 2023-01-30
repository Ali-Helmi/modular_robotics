import robot_comms

comms = robot_comms.robot_comms("/dev/ttyS0", 115200)

# Module addresses
motor_front_left = 0
motor_front_right = 1
motor_rear_left = 2
motor_rear_right = 3
arm_lift = 4
arm_gripper = 5
sensor_left = 6
sensor_right = 7

#motor directions
forward = 0
reverse = 1


def move_robot(direction, speed):
    '''
        Returns 1 if all the motors in the correct mode, -1 if something went wrong

        Check the direction and speed that is requested
        if those values are good, send them to the motors
        Check the returned values from the motors to see if they are in the correct mode
        If any are wrong, tell all motors to stop
    '''
    if direction == 0:
        left_direction = forward
        right_direction = reverse
    elif direction == 1:
        left_direction = reverse
        right_direction = forward
    else:
        return -1

    if speed > 100 or speed < 0:
        return -1
    
    left_check = left_direction ^ speed
    right_check = right_direction ^ speed
    comms.send_frame(motor_front_left, [left_direction, speed, left_check])
    comms.send_frame(motor_front_right, [right_direction, speed, right_check])
    comms.send_frame(motor_rear_left, [left_direction, speed, left_check])
    comms.send_frame(motor_rear_right, [right_direction, speed, right_check])
    # need to add in receiving the frames to check

    return 1

def rotate_robot(direction, speed):
    '''
        Similar to the move robot function, but in this case spins the motors so that
        the robot will spin instead of move
    '''
    pass

def move_arm(angle):
    pass

def toggle_gripper():
    pass

def read_sensor():
    '''
        Requests measured distance from the sensor modules and returns
        a list of the distances
    '''
    
    comms.send_frame(sensor_left, [1])
    distance1 = comms.receive_frame()[0]
    comms.send_frame(sensor_right, [1])
    distance2 = comms.receive_frame()[0]

    return [distance1, distance2]