import math
from PIL import Image
from PIL import ImageDraw
from random import uniform
from time import sleep, time
import TFT as GLCD

LIDP="img/lid/"
EYEP="img/eyes/"
PLATEP="img/plates/"
WHITE=(255,255,255)
BLACK=(0,0,0)

blinking=False # Blinking time
eyeangle=0 # Point of view angle
eyedistance=0 # Distance from center
eyelid=3 # Lid aperture (0..5)
autoblink=True # Set to True if blinking should be automatic
eyes = ["eye01", "eye02", "eye03", "eye04", "eye05", "eye06", "eye07", "eye08", "eye09", "eye10", "eye11", "eye12", "eye13", "eye14", "eye15"]
plates = ["plate1", "plate2", "plate3", "plate4", "plate5", "plate6", "plate7"]
eye = Image.open(EYEP+eyes[0]+".png") # Default eye
plate = Image.open(PLATEP+palets[0]+".png") # Default eye plate
background = WHITE # Default background color
lid = [Image.open(LIDP+"lid0.png"), Image.open(LIDP+"lid01.png"), Image.open(LIDP+"lid2.png"), Image.open(LIDP+"lid3.png"), Image.open(LIDP+"lid4.png"), Image.open(LIDP+"lid5.png")]
# Setup the display    
disp = GLCD.TFT()		# Create TFT LCD display class.
disp.initialize()		# Initialize display.

mpi=math.pi/180

# Create the eye image (i=eye angle [0-360], d=distance from center, lt=lid aperture [0=closed - 5=open, <0 no lid])
def CreateEye(drw,i=0,d=0,lt=3):
    global blinking
    global eye
    global plate
    global lid
    global background
    global mpi
    x=int(math.cos(i*mpi)*d) # Calculates X position for the eye
    y=int(math.sin(i*mpi)*d) # Calculates Y position for the eye
    clear(disp,background) # Clear area using selected background color
    drw.paste(eye, (32+x,32-y), eye) # Drawing the eye in desired position
    drw.paste(plate, (0,0), plate) # Drawing the plate (after the eye, so eye remains invisible if too far from center)
    if (lt>=0): # Lid present only if aperture is not negative
        # Blinking routine
        if (blinking):
            drw.paste(lid[0], (0,0), lid[0]) # Paste lid on the eye
            blinking=Flase
        else:    
            drw.paste(lid[lt], (0,0), lid[lt]) # Paste lid on the eye
    return

# Change eye image
def ChangeEye(n):
    global eye
    if (n>=0) and (n<15):
        eye=Image.open(EYEP+eyes[n]+".png")
    return    

# Change eye plate
def ChangePlate(n):
    global palte
    if (n>=0) and (n<7):
        plate = Image.open(PLATEP+palets[n]+".png")
    return    
    
# Main eye function
def Eye():    
    global disp
    global blinking
    global eyeangle
    global eyedistance
    global eyelid
    global autoblink
    i=uniform(0.8,2.5)
    st=time()
    while True:
        CreateEye(disp,eyeangle,eyedistance,eyelid)
        disp.display()
        if (autoblink):
            if (i<=(time()-st)):
                blinking=True
                i=uniform(0.8,2.5)
                st=time()
