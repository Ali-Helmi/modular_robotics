import multiprocessing
import sys
import os
import platform

import random
from time import sleep

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

def update_objects():
    pass

def update_state():
    pass


def camera(data_queue):
    # runs the computer vision code and sends object and location
    # data to the robot
    
    object = ['ball', 'tape', 'wall']
    # Send random data to the robot module for testing
    while True:
        sleep(random.random() * 2)
        data = [object[random.randint(0,2)], random.randint(1,15)]
        data_queue.put(['cam', data])

def robot(data_queue, log_queue):
    # Collects object and navigation data from camera to move the 
    # robot around and pick up objects
    
    # clear the terminal screen to show formatted data
    if platform.system() == 'Windows':
        os.system('cls')
    elif platform.system() == 'Linux':
        os.system('clear')
        
    last_cam = ''
    last_com = ''
    
    # set up data screen
    print('Camera: ' + last_cam + '\nRobot: ' + last_com + '\nCommand: ', end='')
    
    while True:
        # Collect data from the queue
        data = data_queue.get()
        
        if data[0] == 'cam':
            # reads in data from the camera module. This maintains anything written in the input to not interrupt commands
            last_cam = str(data[1])
            print(SAVE_SPOT + LINE_UP + LINE_UP + LINE_UP + LINE_CLEAR + '\rCamera: ' + last_cam  + LOAD_SPOT, end='')
        elif data[0] == 'com':
            # Displays the last command sent, clears the input line
            last_com = data[1]
            print(LINE_UP +  LINE_UP + LINE_CLEAR + '\rRobot: ' + last_com + '\n' + LINE_CLEAR + 'Command: ', end='')
    pass

def user_interface(data_queue, log_queue):
    # takes user input to send commands to the robot
    sys.stdin = open(0)

    while True:        
        data = input()
        if data == 'quit':
            active = multiprocessing.active_children()
            for child in active:
                if child.name != 'ui':
                    child.close()
        else:
            data_queue.put(['com', data])


if __name__ == '__main__':
    data_queue = multiprocessing.Queue()
    log_queue = multiprocessing.Queue()
    
    camera_proc = multiprocessing.Process(target=camera, args=(data_queue,), name='camera')
    robot_proc = multiprocessing.Process(target=robot, args=(data_queue, log_queue,), name='robot')
    

    camera_proc.start()
    robot_proc.start()

    #camera_proc.join()
    #robot_proc.join()
    #qui_proc.join()

    sys.stdin = open(0)

    while True:        
        data = input()
        if data == 'quit' or data == 'q':
            active = multiprocessing.active_children()
            # should send terminate command to robot to have it shut off any motors running then terminate
            # queue.put(terminate command)
            camera_proc.terminate()
            robot_proc.terminate()
            break
        else:
            data_queue.put(['com', data])

    print('CPUs available: ' + str(multiprocessing.cpu_count()))
