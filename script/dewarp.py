import cv2, thread, time
import numpy as np
import picamera
import picamera.array
from PIL import Image

# Frame size
Ws = 640
Hs = 480
# Center of the donut
Cx = 320
Cy = 240
# Inner donut radius
R1 = 50
# Outer donut radius
R2 = 100

uscita=False

# Initialize PiCamera
camera=picamera.PiCamera()
camera.resolution=(Ws, Hs)
camera.rotation=180
#camera.framerate=0

# Build the unwarp mapping
def buildMap(Ws,Hs,Wd,Hd,R1,R2,Cx,Cy):
    map_x = np.zeros((Hd,Wd),np.float32)
    map_y = np.zeros((Hd,Wd),np.float32)
    for y in range(0,int(Hd-1)):
        for x in range(0,int(Wd-1)):
            r = (float(y)/float(Hd))*(R2-R1)+R1
            theta = (float(x)/float(Wd))*2.0*np.pi
            xS = Cx+r*np.sin(theta)
            yS = Cy+r*np.cos(theta)
            map_x.itemset((y,x),int(xS))
            map_y.itemset((y,x),int(yS))
    return map_x, map_y

# Do the unwarping 
def unwarping(img,xmap,ymap):
    output = cv2.remap(img.getNumpyCv2(),xmap,ymap,cv2.INTER_LINEAR)
    result = Image(output,cv2image=True)
    return result
    
# Get next video frame (cv2 format)   
def GetFrame():
    global camera
    with picamera.array.PiRGBArray(camera) as stream:
        stream.truncate(0)
        camera.capture(stream, format='bgr')
    return stream.array

# Output image size
Wd = 2.0*((R2+R1)/2)*np.pi
Hd = (R2-R1)
# Build unwarping map
xmap,ymap = buildMap(Ws,Hs,Wd,Hd,R1,R2,Cx,Cy)
# First unwarp
img = GetFrame()
#panorama = unwarping(img,xmap,ymap)

def UnWarp():
    global xmap
    global ymap
    global panorama
    global uscita
    while True:
        img = GetFrame()
        panorama = unwarping(img,xmap,ymap)
        if (uscita):
            thread.exit()

def ExitUnwarp():
    uscita=True
