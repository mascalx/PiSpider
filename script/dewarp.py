import cv2, thread, time, urllib
import numpy as np
from PIL import Image

# Frame size
Ws = 320
Hs = 240
# Center of the donut
Cx = 157
Cy = 125
# Inner donut radius
R1 = 60
# Outer donut radius
R2 = 130

uscita=False

# Build the unwarp mapping
def buildMap(Ws,Hs,Wd,Hd,R1,R2,Cx,Cy):
    map_x = np.zeros((Hd,Wd),np.float32)
    map_y = np.zeros((Hd,Wd),np.float32)
    p2=2.0*np.pi
    pm=np.pi/2.0
    Rx=R2-R1
    for y in range(0,int(Hd-1)):
        for x in range(0,int(Wd-1)):
            r = (float(y)/float(Hd))*Rx+R1
            theta = (float(x)/float(Wd))*p2-pm
            xS = Cx+r*np.sin(theta)
            yS = Cy+r*np.cos(theta)
            map_x.itemset((y,x),int(xS))
            map_y.itemset((y,x),int(yS))
    return map_x, map_y

# Do the unwarping 
def unwarping(img,xmap,ymap):
    output = cv2.remap(img,xmap,ymap,cv2.INTER_LINEAR)
    return output
    
# Get next video frame (cv2 format)
# Uses mjpg-streamer to create the video stream
def GetFrame():
    req = urllib.urlopen('http://127.0.0.1:8080/?action=snapshot')
    arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
    image = cv2.imdecode(arr,-1)
    return image

# Output image size
Wd = 2.0*((R2+R1)/2)*np.pi
Hd = (R2-R1)
# Build unwarping map
xmap,ymap = buildMap(Ws,Hs,Wd,Hd,R1,R2,Cx,Cy)
# First unwarp
img = GetFrame()
panorama = unwarping(img,xmap,ymap)

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
