import multiprocessing
import sys
import os
import platform

import random
from time import sleep

#import RPi.GPIO as GPIO

import robot
#import robot_comms

# ANSI commands for moving the cursor arounnd
# https://en.wikipedia.org/wiki/ANSI_escape_code
LINE_UP = '\033[1A'     # Moves the cursor up one line
LINE_CLEAR = '\x1b[2K'  # clears the current line
SAVE_SPOT = '\033[s'    # Saves the current cursor location
LOAD_SPOT = '\033[u'    # restores the saved cursor location
NORMAL = '\033[0m'
UNDERLINE = '\033[4m'
ITALIC = '\033[3m'
BOLD = '\033[1m'

# Command responses
BAD_DIRECTION = -1
BAD_SPEED = -2
BAD_RESPONSE = -3

def update_objects():
    pass

def update_state():
    pass


def fake_cam_data(data_queue):
    object_list = ['ball', 'tape', 'wall']
    # Send random data to the robot module for testing
    while True:
        sleep(random.random() * 2)
        data = []
        for x in range(4):
            data.append([object_list[random.randint(0,2)], random.randint(1,15)])
        data_queue.put(['cam', data])

def camera(data_queue):
    # runs the computer vision code and sends object and location
    # data to the robot
    fake_cam_data(data_queue)
    
    # Real cam data will go here when I get the updated object detection code
    

def robot_controller(data_queue, comms_queue):
    # Collects object and navigation data from camera to move the 
    # robot around and pick up objects
    rb = robot.robot(comms_queue)
    
    # clear the terminal screen to show formatted data
    if platform.system() == 'Windows':
        os.system('cls')
    elif platform.system() == 'Linux':
        os.system('clear')
    
    # set up data screen
    print('Detected objects:\n|' + UNDERLINE + '  TYPE  | DISTANCE ' + NORMAL + '|')
    for x in range(6):
        print('|        |          |')
    print('-----------------------------\nCurrent robot state:\nStopped\n-----------------------------\nCommand: ', end='')
    
    while True:
        # Collect data from the queue
        data = data_queue.get()
        
        if data[0] == 'cam':
            # reads in data from the camera module. This maintains anything written in the input to not interrupt commands
            print_objects(data[1])
        elif data[0] == 'com':
            # Displays the last command sent, clears the input line
            command = data[1].split()
            command_return = 0
            direction = command[0].lower()
            
            state = ''
            
            if direction == 'forward' or direction == 'f':
                command_return = rb.move_robot(rb.MOTOR_FORWARD, int(command[1]))
            elif direction == 'back' or direction == 'b':
                command_return = rb.move_robot(rb.MOTOR_REVERSE, int(command[1]))
            elif direction == 'right' or direction == 'r':
                command_return = rb.rotate_robot(rb.MOTOR_FORWARD, int(command[1]))
            elif direction == 'left' or direction == 'l':
                command_return = rb.rotate_robot(rb.MOTOR_REVERSE, int(command[1]))
            elif direction == 'stop' or direction == 's':
                command_return = rb.stop_robot()
            else:
                state = 'error'
                
            
                
            if rb.state == rb.STOPPED:
                state = 'Stopped'
            elif rb.state == rb.MOVING:
                if rb.direction == rb.FORWARD:
                    state = 'Moving forward at {}%'.format(rb.speed)
                elif rb.direction == rb.REVERSE:
                    state = 'Moving backward at {}%'.format(rb.speed)
                else:
                    state = 'ERROR DIRECTION: {}'.format(rb.direction)
            elif rb.state == rb.ROTATING:
                if rb.direction == rb.CLOCKWISE:
                    state = 'Rotating clockwise at {}%'.format(rb.speed)
                if rb.direction == rb.COUNTERCLOCKWISE:
                    state = 'Rotating counterclockwise at {}%'.format(rb.speed)
            else:
                state = 'ERROR'
                    
            if command_return[0] != 1:
                if command_return[0] == rb.BAD_DIRECTION:
                    state += ' | Bad direction'
                elif command_return[0] == rb.BAD_SPEED:
                    state += ' | Bad speed'
                else:
                    non_respond = []
                    for x in range(1,5):
                        if command_return[x] != 1:
                            non_respond.append(x)
                    
                    state += ' | non-responding motors: {}'.format(non_respond)
            
            print_state(state)
            print_cmd_recv()

def print_objects(objects):
    ui = SAVE_SPOT
    for x in range(10):
        ui += LINE_UP
    ui += '\r'
    
    for item in objects:
        ui += '|  ' + item[0] + '  |   ' + str(item[1]) + '  \n'
    ui += LOAD_SPOT
    print(ui, end='')
    
def print_state(state):
    ui = SAVE_SPOT
    for x in range(3):
        ui += LINE_UP
    ui += LINE_CLEAR + '\r' + state + '\n-----------------------------' + LOAD_SPOT
    print(ui, end='')
    
def print_cmd_recv():
    ui = LINE_UP + LINE_CLEAR + '\rCommand: '
    print(ui, end='')
    
'''
# Probably not going to be used
def uart_receive():
    comms = robot_comms.robot_comms("/dev/ttyS0", 115200, 33)
    frame = comms.receive_frame()
    if frame[0] != -1:
        comms_queue.put(frame)
'''

if __name__ == '__main__':
    # Create queues for passing data
    data_queue = multiprocessing.Queue()
    comms_queue = multiprocessing.Queue()
    
    # Create camera and robot processes
    camera_proc = multiprocessing.Process(target=camera, args=(data_queue,), name='camera')
    robot_proc = multiprocessing.Process(target=robot_controller, args=(data_queue, comms_queue,), name='robot')
    
    # Start camera and robot processes
    camera_proc.start()
    robot_proc.start()

    # reenable input for this process
    sys.stdin = open(0)

    while True:        
        data = input()
        if data == 'quit' or data == 'q':
            active = multiprocessing.active_children()
            # Send the stop command to the robot
            data_queue.put(['com', 's'])
            # Wait for the robot to deal with the stop command
            sleep(.5)
            # Kill all processes and end the program
            camera_proc.terminate()
            robot_proc.terminate()
            
            # Clear the terminal
            #if platform.system() == 'Linux':
            #    os.system('clear')
            
            # Go to a new line so the terminal doesn't end up in a weird spot
            print('')
            break
        else:
            data_queue.put(['com', data])

    #print('CPUs available: ' + str(multiprocessing.cpu_count()))
