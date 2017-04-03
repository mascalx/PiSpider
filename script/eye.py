#!/usr/bin/env python
#-*- coding: utf-8 -*-

import math
from PIL import Image
from PIL import ImageDraw
from PIL import ImageOps
from random import randint
from time import sleep
#import TFT as GLCD

#TFT to RPi connections
# PIN   TFT         RPi
# 1     backlight   (GPIO 26)
# 2     MISO        <none>
# 3     CLK         (GPIO 11)
# 4     MOSI        (GPIO 10)
# 5     CS-TFT      (GPIO 5)
# 6     CS-CARD     <none>
# 7     D/C         (GPIO 6)
# 8     RESET       (none)
# 9     VCC         3V3
# 10    GND         GND

blinkpos=0 # Frame position for eye blinking
blinkdir=1 # Direction of animation (1 -> closing, -1 -> opening)
blinking=False # Blinking time
blinkspd=10 # Speed of blinking
eye = Image.open("eye6.png") # Eye to be frawn
lid = Image.open("lid.png") # Lid base image
# Setup the display    
#disp = GLCD.TFT()		# Create TFT LCD display class.
#disp.initialize()		# Initialize display.
disp=Image.new('RGB', (128, 128)) # ************* remove!
WHITE=(255,255,255)
BLACK=(0,0,0)

def clear(im, color=(0,0,0)): # ************* remove!
		width, height = im.size
		im.putdata([color]*(width*height))    

# Create the eye image (i=eye angle [0-360], d=distance from center, lt=lid aperture [0=open - 100=closed, <0 no lid])
def CreateEye(drw,i=0,d=0,lt=50):
    global blinking
    global blinkdir
    global blinkpos
    global blinkspd
    global eye
    global lid
    we, he = eye.size
    x=math.cos(i*math.pi/180.0)
    y=math.sin(i*math.pi/180.0)
    clear(disp,WHITE)
    drw.paste(eye,(int((128-we)/2)+int(x*d),int((128-he)/2)-int(y*d))) # Drawing the eye in desired position
    if (lt>=0): # Lid present only if aperture is not negative
        # Blinking routine
        if (blinking):
            if (blinkdir>0):
                blinkpos=blinkpos+blinkspd
                if (blinkpos>=(100-lt)):
                    blinkdir=-1
                    blinkpos=100-lt
            else:
                blinkpos=blinkpos-blinkspd
                if (blinkpos<blinkspd):
                    blinkdir=1
                    blinking=False
                    blinkpos=0
        ld=lid.copy() # Get lid base image
        ld = lid.point(lambda p: p > int((lt+blinkpos)*2.55) and 255) # Convert to mask
        drw.paste(ld, (0,0), ImageOps.invert(ld)) # Paste mask on the eye
    return
    
# Main eye function
def Eye():    
    global disp
    i=randint(50,200)
    while True:
        CreateEye(disp,0,0,50)
#        disp.display()
        #disp.save("result%i.png"%i)
        i=i-1
        if (i==0):
            blinking=True
            i=randint(50,200)
        sleep(0.01)    
        
# Main program
if __name__ == '__main__':
    Eye()
