import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

GPIO.setup(5, GPIO.OUT)
GPIO.setup(6, GPIO.IN)

print('starting')

while 1:
    GPIO.output(5, 1)
    time.sleep(10/1000000)
    GPIO.output(5, 0)

    while(not GPIO.input(6)):
        continue

    start = time.time_ns()

    while(GPIO.input(6)):
        continue

    end = time.time_ns()

    distance = ((end - start) / 1000) / 148

    print('\rDistance: ', distance, '\t\t', end='\r')
    
    #print('Distance: ', distance, ' in')
    
    if distance > 40:
        break
    
    time.sleep(0.1)

GPIO.cleanup()