#!/usr/bin/env python
#-*- coding: utf-8 -*-

#********************************************************************
# PiSpider v0.1
# Control system for modified Xpider Ballsy by Roboeve
#
# Sensors:
#     Camera 360°
#         - Brightest spot direction (-180..+180)
#         - Brightest spot elevation (0..90)
#         - Ambient light (0..100)
#         - Face detection (dir and elev of first detected face)
#     Left digital bumper (0..1)
#     Right digital bumper (0..1)
#     Low battery (0..1) 1 means battery ok
#
# Actuators:
#     Legs motor (-100..+100)
#     Head rotation motor (-100..+100)
#
# Other:
#     TFT display for eye simulation
#     Backlight for TFT (0..100)
#********************************************************************

import thread, time, cv2
import numpy as np
from gpiozero import Motor, PWMLED, Button

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
M_FWD = 20 # GPIO5 pin for forward movement
M_BWD = 21 # GPIO6 pin for backward movement
M_CKW = 5 # GPIO20 pin for clockwise rotation
M_CCW = 6 # GPIO21 pin for counterclockwise rotation
BLIGHT = 12 # GPIO12 pin for TFT backlight control
LBUMP = 19 # GPIO19 pin for left bumper sensor
RBUMP = 26 # GPIO26 pin for right bumper sensor
LBO = 13 # Low battery alarm
ANG_SPD = 100 # Angular speed for head rotation
Facing = 0 # Current direction (approximate)

# Actuators creation
motor = Motor(M_FWD, M_BWD, pwm=True)
motor.frequency = 500
head = Motor(M_CKW, M_CCW, pwm=True)
head.frequency = 500
backlight = PWMLED(BLIGHT, frequency=250)
l_bump = Button(LBUMP)
r_bump = Button (RBUMP)
low_batt = Button(LBO,pull_up=False)

# Face and cat detectors
face_cascade = cv2.CascadeClassifier('face.xml')
cat_cascade = cv2.CascadeClassifier('cat.xml')

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
    x=maxLoc[0]
    y=maxLoc[1]
    d=np.sqrt(np.square(cx-x)+np.square(cy-y)) # Distance from center
    a=np.arctan2((y-cy),(x-cx))/eyelib.mpi # Angle (-180..180)
    return a,d,maxVal

# Returns the average luminosity of the (CV2) image (0..100)
def AverageBrightness(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return int(np.mean(gray)/2.55)

# Returns list of frontal faces (angle,elevation)
def GetFaces(img):    
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    lista = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, flags=cv2.CASCADE_SCALE_IMAGE)
    faces=[]
    for (x,y,w,h) in lista:
        fx=(x+(w/2.0)-298)*180.0/298.0
        fy=y+(h/2)
        faces.append([fx,fy])
    return faces
    
# Returns list of frontal cats faces (angle,elevation)
def GetCats(img):    
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    lista = cat_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, flags=cv2.CASCADE_SCALE_IMAGE)
    cats=[]
    for (x,y,w,h) in lista:
        fx=(x+(w/2.0)-298)*180.0/298.0
        fy=y+(h/2)
        cats.append([fx,fy])
    return cats

# Set (horizontal) looking angle for the eye
def LookAt(a):
    if (a<5):
        eyelib.eyeangle=90
        eyelib.eyedistance=int(-a/2)
        if (eyelib.eyedistance>20):
            eyelib.eyedistance=20
    elif (a>5):
        eyelib.eyeangle=270
        eyelib.eyedistance=int(a/2)
        if (eyelib.eyedistance>20):
            eyelib.eyedistance=20
    else:
        eyelib.eyedistance=0
    return

# Main program
if __name__ == '__main__':
    backlight.value=1 # Start with backlight at full brightness
    motor.stop() # Be sure the robot is not moving
    head.stop() # Be sure the robot is not moving
    
    thread.start_new_thread(eyelib.Eye, ()) # Eye thread
    thread.start_new_thread(dewarp.UnWarp, ()) # Unwarping thread
    
#    while True: # Loop forever
#        if (r_bump.is_pressed):
#            print "bump!"
#        if (low_batt.value==0): # If battery is low, just stop the motors and exit
#            print "Battery low!"
#            motor.stop()
#            head.stop()
#            backlight.value=0
#            break            
#        a,d,v=FindBrightestSpot(dewarp.img,dewarp.Cx,dewarp.Cy) # Get brightest spot data
#        pano=dewarp.panorama.copy() # Get copy of the unwarped image
#        faces=GetFaces(pano) # Detect human faces (frontal)
#        cats=GetCats(pano) # Detect feline faces (frontal)
#        if (faces): # face(s) detected
#            for (x,y) in faces:
#                LookAt(x)
#        elif (cats): # no humans, but cats have been detected
#            for (x,y) in cats:
#                LookAt(x)
#        else: # no beings to interact with so search for light
#            LookAt(a)
    
# !!!! DELETE AFTER GETTING DATA
# Lines below are just for gathering some data in order to calculate the ANG_SPD value
dewarp.img=dewarp.GetFrame() # Get new frame
a,d,v=FindBrightestSpot(dewarp.img,dewarp.Cx,dewarp.Cy) # Get brightest spot data
print a,d,v
cv2.imwrite("im1.jpg",dewarp.img)
Rotate (10,1)
time.sleep(1000)
dewarp.img=dewarp.GetFrame() # Get new frame
a,d,v=FindBrightestSpot(dewarp.img,dewarp.Cx,dewarp.Cy) # Get brightest spot data
print a,d,v
cv2.imwrite("im2.jpg",dewarp.img)
