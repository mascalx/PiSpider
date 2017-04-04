#!/usr/bin/env python
#-*- coding: utf-8 -*-

import thread, time
import numpy as np
from gpiozero import Motor, PWMLED

# Eyelib can be managed by following variables:
#    blinking : If True start a blink animation (1 cycle)
#    blinkspd : Speed of blinking
#    eye : Eye image
#    lid : Lid base image
import eyelib

# Last dewarped frame can be accessed by using variable "panorama"
# A copy should be used to access data in order to avoid in-between garbage
import dewarp

# Constants
M_FWD = 0 # GPIO pin for forward movement
M_BWD = 0 # GPIO pin for backward movement
M_CKW = 0 # GPIO pin for clockwise rotation
M_CCW = 0 # GPIO pin for counterclockwise rotation
BLIGHT = 0 # GPIO pin for TFT backlight control
ANG_SPD = 0 # Angular speed for head rotation
Facing = 0 # Current direction (approximate)

# Actuators creation
motor = Motor(M_FWD, M_BWD, pwm=True)
head = Motor(M_CKW, M_CCW, pwm=True)
backlight = PWMLED(BLIGHT)

# Move the spider forward or backward. Speed -1..0 = backward, 0..1 = forward
def Move(spd):
    if (spd>0):
        motor.forward(spd)
    else:
        motor.backward(abs(spd))
    if (spd==0):
        motor.stop()
        
# Rotate the head. Angle is the approximate rotation (0..360). Speed -1..0 = counterclockwise, 0..1 = clockwise        
def Rotate(angle,spd):   
    global Facing
    if (spd>0):
        head.forward(spd)
    else:
        head.backward(abs(spd))
    if (spd<>0):    
        time.sleep(ANG_SPD(angle/abs(spd)))
    head.stop()    
    Facing=(Facing-(angle*(np.sign(spd))))%360

# Main program
if __name__ == '__main__':
    backlight.value=1 # Start with backlight at full brightness
    motor.stop() # Be sure the robot is not moving
    head.stop() # Be sure the robot is not moving
    
    thread.start_new_thread(Eye, ()) # Eye thread
    thread.start_new_thread(UnWarp, ()) # Unwarping thread
    
    while True: # Loop forever
        pass
