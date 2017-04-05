import math
from PIL import Image
from PIL import ImageDraw
from PIL import ImageOps
from random import randint
from time import sleep
import TFT as GLCD

blinkpos=0 # Frame position for eye blinking
blinkdir=1 # Direction of animation (1 -> closing, -1 -> opening)
blinking=False # Blinking time
blinkspd=10 # Speed of blinking
eyeangle=0 # Point of view angle
eyedistance=0 # Distance from center
eyelid=50 # Lid aperture (0..100)
autoblink=True # Set to True if blinking should be automatic
eye = Image.open("img/eye6.png") # Eye to be frawn
lid = Image.open("img/lid.png") # Lid base image
# Setup the display    
disp = GLCD.TFT()		# Create TFT LCD display class.
disp.initialize()		# Initialize display.
WHITE=(255,255,255)
BLACK=(0,0,0)

mpi=math.pi/180

# Create the eye image (i=eye angle [0-360], d=distance from center, lt=lid aperture [0=open - 100=closed, <0 no lid])
def CreateEye(drw,i=0,d=0,lt=50):
    global blinking
    global blinkdir
    global blinkpos
    global blinkspd
    global eye
    global lid
    global mpi
    we, he = eye.size
    x=int(math.cos(i*mpi)*d)
    y=int(math.sin(i*mpi)*d)
    clear(disp,WHITE)
    drw.paste(eye,(((128-we)>>1)+x,((128-he)>>1)-y)) # Drawing the eye in desired position
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
        ltb=int((lt+blinkpos)*2.55)
        ld = lid.point(lambda p: p > ltb and 255) # Convert to mask
        drw.paste(ld, (0,0), ImageOps.invert(ld)) # Paste mask on the eye
    return
    
# Main eye function
def Eye():    
    global disp
    global blinking
    global eyeangle
    global eyedistance
    global eyelid
    global autoblink
    i=randint(2,20)
    while True:
        CreateEye(disp,eyeangle,eyedistance,eyelid)
        disp.display()
        if (autoblink):
            i=i-1
            if (i==0):
                blinking=True
                i=randint(2,20)
