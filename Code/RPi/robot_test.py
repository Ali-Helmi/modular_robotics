import robot
import robot_comms
from multiprocessing import Queue
#import serial

#ser = serial.Serial("/dev/ttyS0", 115200)

comm_queue = Queue()


rb = robot.robot(comm_queue)

#rb.comms.ser.add

print('Going')

print(rb.move_robot(1, 10))
print('State: {}, Direction: {},  Speed: {}'.format(rb.state, rb.direction, rb.speed))

print(rb.move_robot(1, 40))
print('State: {}, Direction: {},  Speed: {}'.format(rb.state, rb.direction, rb.speed))

print(rb.move_robot(2, 60))
print('State: {}, Direction: {},  Speed: {}'.format(rb.state, rb.direction, rb.speed))

print(rb.move_robot(2, 120))
print('State: {}, Direction: {},  Speed: {}'.format(rb.state, rb.direction, rb.speed))

print(rb.move_robot(7, 120))
print('State: {}, Direction: {},  Speed: {}'.format(rb.state, rb.direction, rb.speed))


