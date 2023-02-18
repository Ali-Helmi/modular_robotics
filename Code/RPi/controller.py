import multiprocessing
import sys
import os
import platform

import random
from time import sleep

from ObjectDetection import object_detection

#import RPi.GPIO as GPIO

import robot
#import robot_comms

# ANSI commands for moving the cursor arounnd
# https://en.wikipedia.org/wiki/ANSI_escape_code
LINE_UP = '\033[{}A'     # Moves the cursor up one line
LINE_DOWN = '\033[{}B'   # Moves cursor down one line
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

previous_objects = []

def update_objects():
    pass

def update_state():
    pass


def fake_cam_data(data_queue):
    object_list = ['ball', 'tape']
    # Send random data to the robot module for testing
    while True:
        sleep(random.random() * 2)
        data = []
        for x in range(4):
            obj = {
                'name' : object_list[random.randint(0,1)], 
                'xcoord' : random.randint(1,15), 
                'ycoord' : random.randint(1,15)
                }
            data.append(obj)
            
        data_queue.put(['cam', data])


def camera(data_queue):
    # runs the computer vision code and sends object and location
    # data to the robot
    #fake_cam_data(data_queue)
    
    # Real cam data will go here when I get the updated object detection code
    object_detection.object_detections(data_queue)
    
def format_camera_objects(objects):
    '''
    obj = {
        'name'      : 'ball',
        'xcoord'    : location_x,
        'ycoord'    : location_y,
        'llx'       : x,
        'lly'       : y,
        'w'         : w,
        'h'         : h
    }
    '''
    '''
    if len(previous_objects) == 0:
        for obj in objects:
            previous_objects.append(obj)
        pass
    else:
    ''' 
    
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
    print('Detected objects:\n|' + UNDERLINE + '  TYPE  | X Coord | Y Coord | Size ' + NORMAL + '|')
    for x in range(6):
        print('|        |          |')
    print('-----------------------------\nCurrent robot state:\nStopped\n-----------------------------\nCommand: ', end='')
    
    found_objects = []
    
    searching = False
    
    while True:
        # Collect data from the queue
        data = data_queue.get()
        
        if data[0] == 'cam':
            # reads in data from the camera module.
            found_objects = data[1]
            print_objects(data[1])
            
            #format_camera_objects(data[1])
            
        elif data[0] == 'com':
            # Displays the last command sent, clears the input line
            command = data[1].split()
            command_return = 0
            direction = command[0].lower()
            
            state = ''
            
            # Check the command and call the correct function
            if direction == 'forward' or direction == 'f':
                searching = False
                command_return = rb.move_robot(rb.FORWARD, int(command[1]))
            elif direction == 'back' or direction == 'b':
                searching = False
                command_return = rb.move_robot(rb.REVERSE, int(command[1]))
            elif direction == 'right' or direction == 'r':
                searching = False
                command_return = rb.rotate_robot(rb.CLOCKWISE, int(command[1]))
            elif direction == 'left' or direction == 'l':
                searching = False
                command_return = rb.rotate_robot(rb.COUNTERCLOCKWISE, int(command[1]))
            elif direction == 'stop' or direction == 's':
                searching = False
                command_return = rb.stop_robot()
            elif direction == 'search':
                searching = True
                command_return = [1]
            else:
                state += ' | ERROR: BAD COMMAND'
                command_return = [1]
            
            
            # Check for errors in command responses
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
            
            print_state(rb, state, 1)
            print_cmd_recv()
            
        if (searching):
            if search_for_ball(rb, found_objects):
                searching = False
            
            
            
def search_for_ball(rb : robot.robot, objects):
    if len(objects) > 0:
        ball = objects[0]
        
        size = ball['w'] * ball['h']
        if ball['xcoord'] > 340:
            # Rotate the robot so that the ball moves to the center of the frame
            if rb.state == rb.ROTATING and rb.direction == rb.CLOCKWISE:
                pass
            else:
                rb.stop_robot()
                rb.rotate_robot(rb.CLOCKWISE, 10)
        elif ball['xcoord'] < 300:
            # Rotate the robot so that the ball moves to the center of the frame
            if rb.state == rb.ROTATING and rb.direction == rb.COUNTERCLOCKWISE:
                pass
            else:
                rb.stop_robot()
                rb.rotate_robot(rb.COUNTERCLOCKWISE, 10)
        elif size < 27000:
            # Move the robot forward until the ball is the desired size
            if rb.state == rb.MOVING and rb.direction == rb.FORWARD:
                pass
            else:
                rb.stop_robot()
                rb.move_robot(rb.FORWARD, 10)
        else:
            rb.stop_robot()
            print_state(rb, ' | Done searching', 0)
            #print_cmd_recv()
            return 1
        
        print_state(rb, ' | Searching ' + str(size), 0)
        #print_cmd_recv()
        
    return 0
            
    

def print_objects(objects):
    ui = SAVE_SPOT
    #for x in range(5):
    ui += LINE_UP.format(4)
        
    for x in range(6):
        ui += LINE_UP.format(1) + LINE_CLEAR
    ui += '\r'
    
    
    
    for item in objects:
        #ui += '|  ' + item[0] + '  |   ' + str(item[1]) + '  \n'
        ui += '|  ' + item['name'] + '  |   ' + str(item['xcoord']) + '   |   ' + str(item['ycoord']) + '   | ' + str(item['w'] * item['h']) + ' |\n'
    ui += LOAD_SPOT
    print(ui, end='')
    
    
def print_state(rb : robot.robot, ext_state, command):
    # Check the current robot state and add it to the status'
    state = ''
    if rb.state == rb.STOPPED:
        state += 'Stopped'
    elif rb.state == rb.MOVING:
        if rb.direction == rb.FORWARD:
            state += 'Moving forward at {}%'.format(rb.speed)
        elif rb.direction == rb.REVERSE:
            state += 'Moving backward at {}%'.format(rb.speed)
        else:
            state += 'ERROR DIRECTION: {}'.format(rb.direction)
    elif rb.state == rb.ROTATING:
        if rb.direction == rb.CLOCKWISE:
            state += 'Rotating clockwise at {}%'.format(rb.speed)
        if rb.direction == rb.COUNTERCLOCKWISE:
            state += 'Rotating counterclockwise at {}%'.format(rb.speed)
    else:
        state = 'ERROR'
        
    state += ext_state
    
    ui = SAVE_SPOT
    
    if command:
        ui += LINE_UP.format(3)
    else:
        ui += LINE_UP.format(2)
        
    ui += LINE_CLEAR + '\r' + state + '\n-----------------------------' + LOAD_SPOT
    print(ui, end='')
    
    
def print_cmd_recv():
    ui = LINE_UP.format(1) + LINE_CLEAR + '\rCommand: '
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
