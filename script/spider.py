#!/usr/bin/env python
#-*- coding: utf-8 -*-

import thread, time, cv2
import numpy as np
from gpiozero import Motor, PWMLED

# Eyelib can be managed by following variables:
#    blinking : If True start a blink animation (1 cycle)
#    eyeangle : Direction of view
#    eyedistance : Distance of pupil from center
#    eyelid : Lid aperture (0=full close..5=full open, <0=no lid)
#    autoblink : If True blinking is automatic
#    background : background color
#    ChangeEye(n) : Change the drawn eye (n=0..14)
#    ChangePlate(n) : Change the drawn plate (n=0..6)
import eyelib

# Last dewarped frame can be accessed by using variable "panorama"
# A copy should be used to access data in order to avoid in-between garbage
#    panorama : the unwarped image
#    img : the last captured frame
#    GetFrame() : Function to get a new frame
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
        time.sleep(ANG_SPD*(angle/abs(spd)))
    head.stop()    
    Facing=(Facing-(angle*(np.sign(spd))))%360
    
# Returns the angles of the brightest spot in the (CV2) image (a = angle [-180..180], d = radius, maxVal = intensity)
def FindBrightestSpot(img,cx,cy):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (11, 11), 0)
    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(gray)
    x,y,v=FindBrightestSpot(img) # Get brightest spot data
    x=maxLoc[0]
    y=maxLoc[1]
    d=np.sqrt(np.sqr(cx-x)+np.sqr(cy-y)) # Distance from center
    a=np.arctan2((y-cy),(x-cx))/eyelib.mpi # Angle (-180..180)
    return a,d,maxVal

# Returns the average luminosity of the (CV2) image
def AverageBrightness(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return np.mean(gray)

# Main program
if __name__ == '__main__':
    backlight.value=1 # Start with backlight at full brightness
    motor.stop() # Be sure the robot is not moving
    head.stop() # Be sure the robot is not moving
    
    thread.start_new_thread(eyelib.Eye, ()) # Eye thread
    #thread.start_new_thread(dewarp.UnWarp, ()) # Unwarping thread
    
    while True: # Loop forever
        dewarp.img=dewarp.GetFrame() # Get new frame
        bright=AverageBrightness(dewarp.img) # Get ambient light
        a,d,v=FindBrightestSpot(dewarp.img,dewarp.Cx,dewarp.Cy) # Get brightest spot data
