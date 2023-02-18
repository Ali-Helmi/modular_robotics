import multiprocessing
import robot_comms
from time import sleep
from datetime import datetime

# Module addresses
motor_front_left =  1
motor_front_right = 2
motor_rear_left =   3
motor_rear_right =  4
arm_lift =          5
arm_gripper =       6
sensor_left =       7
sensor_right =      8



class robot:
    def __init__(self, comms_queue : multiprocessing.Queue) -> None:
        # Motor directions
        self.MOTOR_FORWARD = 1
        self.MOTOR_REVERSE = 2
        self.MOTOR_COAST = 3

        # States
        self.STOPPED = 1
        self.MOVING = 2
        self.ROTATING = 3
        self.FORWARD = 5
        self.REVERSE = 6
        self.CLOCKWISE = 7
        self.COUNTERCLOCKWISE = 8
        self.ERROR = 9
        
        # Errors
        self.BAD_DIRECTION =    -1
        self.BAD_SPEED =        -2
        self.UART_ERROR =       -4
        
        self.comms = robot_comms.robot_comms("/dev/ttyS0", 115200, 33)
        self.state = self.STOPPED
        self.direction = self.STOPPED
        self.speed = 0
        self.comms_queue = comms_queue

  
    def motor_frame_to_dict(self, frame):
        return {
            'address'   : frame[0],
            'check'     : frame[1],
            'direction' : frame[2],
            'speed'     : frame[3]
        }
        

    def send_motor_commands(self, send_data):
        # Clear any data in the serial input
        self.comms.flush_input()
        
        # Send frames to each motor
        self.comms.send_frame(motor_front_left, [send_data['leftdir'], send_data['speed'], send_data['leftcheck']])
        sleep(0.001)
        self.comms.send_frame(motor_front_right, [send_data['rightdir'], send_data['speed'], send_data['rightcheck']])
        sleep(0.001)
        self.comms.send_frame(motor_rear_left, [send_data['leftdir'], send_data['speed'], send_data['leftcheck']])
        sleep(0.001)
        self.comms.send_frame(motor_rear_right, [send_data['rightdir'], send_data['speed'], send_data['rightcheck']])
        
        # Grab responses
        responses = []
        
        for x in range(4):
            responses.append(self.comms.receive_frame(self.comms.MOTOR_FRAME))
            
        return responses
        return 1
  
    
    def check_responses(self, sent_data, received_data):
        
        response_recieved = [0, 0, 0, 0]
                
        for frame in received_data:
            
            # If the sent and received data matches up, 
            # set a motor's response to 1
            if frame[0] > 0:
                frame_dict = self.motor_frame_to_dict(frame)
            
                if frame_dict['address'] == 1 or frame_dict['address'] == 3:
                    # Check the left motors
                    if frame_dict['direction'] == sent_data['leftdir']:
                        # Check the direction
                        if frame_dict['speed'] == sent_data['speed']:
                            # Check the check value
                            if frame_dict['check'] == sent_data['leftcheck']:
                                response_recieved[frame_dict['address'] - 1] = 1
                
                if frame_dict['address'] == 2 or frame_dict['address'] == 4:
                    # Check the right motors
                    if frame_dict['direction'] == sent_data['rightdir']:
                        # Check the direction
                        if frame_dict['speed'] == sent_data['speed']:
                            # Check the check value
                            if frame_dict['check'] == sent_data['rightcheck']:
                                response_recieved[frame_dict['address'] - 1] = 1
                                
        return response_recieved
        return 1

    def stop_robot(self):
        '''
            Sends the coast command to every motor to stop the robot 
        '''
        direction = self.MOTOR_COAST
        speed = 1
        check = direction ^ speed
        
        sent_data = {
           'leftdir'    : direction,
           'rightdir'   : direction,
           'speed'      : speed,
           'leftcheck'  : check,
           'rightcheck' : check
        }
        
        responses = self.send_motor_commands(sent_data)
        
        checked_responses = self.check_responses(sent_data, responses)
        
        comm_error = False
        
        for resp in checked_responses:
            if resp != 1:
                comm_error = True
                
        if comm_error:
            self.state = self.ERROR
            self.direction = self.ERROR
            self.speed = self.ERROR
            
            with open('rblog.tx', 'w') as f:
                for item in sent_data:
                    f.write(str(sent_data[item]))
                    f.write('\n')
                for resp in responses:
                    f.write(str(resp))
                    f.write('\n')
            return [self.UART_ERROR] + checked_responses
        else:
            self.state = self.STOPPED
            self.speed = 0
            self.direction = self.STOPPED
            return [1]

        

    def move_robot(self, direction, speed):      
        '''
            Sends commands to each motor the move the robot forward or backward
        '''
        if direction == self.FORWARD:
            left_direction = self.MOTOR_FORWARD
            right_direction = self.MOTOR_REVERSE
        elif direction == self.REVERSE:
            left_direction = self.MOTOR_REVERSE
            right_direction = self.MOTOR_FORWARD
        else:
            return [self.BAD_DIRECTION]

        if speed > 100 or speed < 0:
            return [self.BAD_SPEED]
        
        left_check = left_direction ^ speed
        right_check = right_direction ^ speed
        
        sent_data = {
           'leftdir'    : left_direction,
           'rightdir'   : right_direction,
           'speed'      : speed,
           'leftcheck'  : left_check,
           'rightcheck' : right_check
        }
        
        responses = self.send_motor_commands(sent_data)
        
        checked_responses = self.check_responses(sent_data, responses)
        
        comm_error = False
        
        for resp in checked_responses:
            if resp != 1:
                comm_error = True
                
        if comm_error:
            self.stop_robot()
            return [self.UART_ERROR] + checked_responses
        else:
            self.state = self.MOVING
            self.speed = speed
            if direction == self.FORWARD:
                self.direction = self.FORWARD
            elif direction == self.REVERSE:
                self.direction = self.REVERSE
            return [1]
        
        return 1
    

    def rotate_robot(self, direction, speed):
        '''
            Sends commands to each motor to rotate the robot left or right
        '''
        
        if direction == self.CLOCKWISE:
            rotate_direction = self.MOTOR_FORWARD
        elif direction == self.COUNTERCLOCKWISE:
            rotate_direction = self.MOTOR_REVERSE
        else:
            return self.BAD_DIRECTION
        
        if speed > 100 or speed < 0:
            return self.BAD_SPEED
        
        check = rotate_direction ^ speed
        
        sent_data = {
           'leftdir'    : rotate_direction,
           'rightdir'   : rotate_direction,
           'speed'      : speed,
           'leftcheck'  : check,
           'rightcheck' : check
        }
        
        responses = self.send_motor_commands(sent_data)
        
        checked_responses = self.check_responses(sent_data, responses)
        
        comm_error = False
        
        for resp in checked_responses:
            if resp != 1:
                comm_error = True
                
        if comm_error:
            self.stop_robot()
            return [self.UART_ERROR] + checked_responses
        else:
            self.state = self.ROTATING
            self.speed = speed
            if direction == self.CLOCKWISE:
                self.direction = self.CLOCKWISE
            elif direction == self.COUNTERCLOCKWISE:
                self.direction = self.COUNTERCLOCKWISE
            return [1]
        
        return 1

    def move_arm(self, angle):
        pass

    def toggle_gripper(self):
        pass

    def read_sensor(self):
        '''
            Requests measured distance from the sensor modules and returns
            a list of the distances
        '''
        
        self.comms.send_frame(sensor_left, [1])
        distance1 = self.comms.receive_frame()[0]
        self.comms.send_frame(sensor_right, [1])
        distance2 = self.comms.receive_frame()[0]

        return [distance1, distance2]