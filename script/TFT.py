import numbers
import time
from PIL import Image
from PIL import ImageDraw
import RPi.GPIO as GPIO
import spidev as spi

spi = spi.SpiDev()

TFT_WIDTH    = 128 # Screen Width
TFT_HEIGHT   = 128 # Scree Height

NOP         = 0x00
SWRESET     = 0x01
RDDID       = 0x04
RDDST       = 0x09
RDDPM       = 0x0A
RDDMADCTL   = 0x0B
RDDCOLMOD   = 0x0C
RDDIM       = 0x0D
RDDSM       = 0x0E
RDDSDR      = 0x0F
SLEEP_IN    = 0x10
SLEEP_OUT   = 0x11
PTLON       = 0x12
NORON       = 0x13
INVOFF      = 0x20
INVON       = 0x21
GAMSET      = 0x26
DISPOFF     = 0x28
DISPON      = 0x29
CASET       = 0x2A
RASET       = 0x2B
RAMWR       = 0x2C
RGBSET      = 0x2D
RAMRD       = 0x2E
PTLAR       = 0x30
SCRLAR      = 0x33
TEOFF       = 0x34
TEON        = 0x35
MADCTL      = 0x36
VSCSAD      = 0x37
IDLE_MODE_OFF = 0x38
IDLE_MODE_ON  = 0x39
COLMOD      = 0x3A
RDID1       = 0xDA
RDID2       = 0xDB
RDID3       = 0xDC
FRMCTR1     = 0xB1
FRMCTR2     = 0xB2
FRMCTR3     = 0xB3
INVCTR      = 0xB4
DISSET5     = 0xB6 
PWCTR1      = 0xC0
PWCTR2      = 0xC1
PWCTR3      = 0xC2
PWCTR4      = 0xC3
PWCTR5      = 0xC4
VMCTR1      = 0xC5
VMOFCTR     = 0xC7
WRID2       = 0xD1
WRID3       = 0xD2
NVFCTR1     = 0xD9
NVFCTR2     = 0xDE
NVFCTR3     = 0xDF
GMCTRP1     = 0xE0
GMCTRN1     = 0xE1
GCV         = 0xFC
DUMMY       = 0xff

BLACK = 0x0000
BLUE = 0x001F
RED = 0xF800
GREEN = 0x07E0
CYAN = 0x07FF
MAGENTA = 0xF81F
YELLOW = 0xFFE0  
WHITE = 0xFFFF

MADCTL_MY = 0x80
MADCTL_MX = 0x40
MADCTL_MV = 0x20
MADCTL_ML = 0x10
MADCTL_MH = 0x04

MADCTL_M1 = 0x00
MADCTL_M2 = 0b10000000
MADCTL_M3 = 0b01000000
MADCTL_M4 = 0b11000000
MADCTL_M5 = 0b00100000
MADCTL_M6 = 0b10100000
MADCTL_M7 = 0b01100000
MADCTL_M8 = 0b11100000

MADCTL_RGB = 0x00
MADCTL_BGR = 0x08

GAMMA1 = 0x01
GAMMA2 = 0x02
GAMMA3 = 0x04
GAMMA4 = 0x08

PIXEL12BIT = 0x03
PIXEL16BIT = 0x05
PIXEL18BIT = 0x06

DC = 22
CE = 0
RST = 18
TFT_CS = 8

ON = 1
OFF = 0

def color565(r, g, b):
    return ((b & 0xF8) << 8) | ((g & 0xFC) << 3) | (r >> 3)

def image_to_data(image):
    pixels = image.convert('RGB').load()
    width, height = image.size
    for y in range(height):
        for x in range(width):
            r,g,b = pixels[(x,y)]
            color = color565(r, g, b)
            yield (color >> 8) & 0xFF
            yield color & 0xFF

class TFT(object):
    def __init__(self):
        self.dc = DC
        self.ce = CE
        self.rst = RST
        self.cs = TFT_CS
        self.width = TFT_WIDTH
        self.height = TFT_HEIGHT
        spi.open(0,self.ce)
        spi.max_speed_hz = int(24000000)
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)	
        GPIO.setup(self.cs, GPIO.OUT)
        GPIO.setup(self.dc, GPIO.OUT)
        GPIO.setup(self.rst, GPIO.OUT)	
        self.CE_DESELECT()
        self.buffer = Image.new('RGB', (self.width, self.height))	# Create an image buffer.
	
    def CE_SELECT(self):
        GPIO.output(self.cs, 0)
			
    def CE_DESELECT(self):
        GPIO.output(self.cs, 1)

    def send(self, data, dataOrCmd=True, length=4096):
        # Set DC low for command, high for data.
        GPIO.output(self.dc, dataOrCmd)
        # Convert scalar argument to list so either can be passed as parameter.
        if isinstance(data, numbers.Number):
            data = [data & 0xFF]
        # Write data a chunk at a time.
        for start in range(0, len(data), length):
            end = min(start+length, len(data))
            spi.writebytes(data[start:end])

    def command(self, data):
        self.CE_SELECT()	
        self.send(data, False)
        self.CE_DESELECT()	

    def data(self, data):
        self.CE_SELECT()	
        self.send(data, True)
        self.CE_DESELECT()	

    def reset(self):
        if self._rst is not None:
            GPIO.output(self.rst,1)
            time.sleep(0.005)
            GPIO.output(self.rst,0)
            time.sleep(0.02)
            GPIO.output(self.rst,1)
            time.sleep(0.150)

    def initialize(self):
        GPIO.setup(self.dc, GPIO.OUT)
        GPIO.setup(self.rst, GPIO.OUT)
        GPIO.setup(TFT_CS, GPIO.OUT)
        GPIO.output(self.dc, 0)
        GPIO.output(self.rst, 1)
        self.command(SWRESET) 
        time.sleep(0.015)
        self.command(SLEEP_OUT) 
        time.sleep(0.60)
        self.command(FRMCTR1)
        self.data(0x01) 
        self.data(0x2C) 
        self.data(0x2D) 
        self.command(FRMCTR2) 
        self.data(0x01) 
        self.data(0x2C) 
        self.data(0x2D) 
        self.command(FRMCTR3) 
        self.data(0x01) 
        self.data(0x2C) 
        self.data(0x2D) 
        self.data(0x01) 
        self.data(0x2C) 
        self.data(0x2D) 
        self.command(INVCTR)
        self.data(0x07)
        self.command(PWCTR1) 
        self.data(0xA2) 
        self.data(0x02) 
        self.data(0x84) 
        self.command(PWCTR2) 		
        self.data(0XC5) 
        self.command(PWCTR3)
        self.data(0x0A) 
        self.data(0x00) 
        self.command(PWCTR4)
        self.data(0x8A) 
        self.data(0x2A) 
        self.command(PWCTR5) 
        self.data(0x8A) 
        self.data(0xEE) 
        self.command(VMCTR1)
        self.data(0x0E) 
        self.command(INVOFF) 
        self.command(MADCTL)
        self.data(0xC0) 
        self.command(COLMOD)
        self.data(0x05) 
        self.command(CASET) 
        self.data(0x00) 
        self.data(0x7F) 
        self.command(RASET) 
        self.data(0x00) 
        self.data(0x9F) 
        self.command(GMCTRP1)
        self.data(0x02) 
        self.data(0x1c) 
        self.data(0x07) 
        self.data(0x12) 
        self.data(0x37) 
        self.data(0x32) 
        self.data(0x29) 
        self.data(0x2d) 
        self.data(0x29) 
        self.data(0x25) 
        self.data(0x2B) 
        self.data(0x39) 
        self.data(0x00) 
        self.data(0x01) 
        self.data(0x03) 
        self.data(0x10) 
        self.command(GMCTRN1) 
        self.data(0x03) 
        self.data(0x1d) 
        self.data(0x07) 
        self.data(0x06) 
        self.data(0x2E) 
        self.data(0x2C) 
        self.data(0x29) 
        self.data(0x2D) 
        self.data(0x2E) 
        self.data(0x2E) 
        self.data(0x37) 
        self.data(0x3F) 
        self.data(0x00) 
        self.data(0x00) 
        self.data(0x02) 
        self.data(0x10) 
        self.command(NORON)
        time.sleep(0.100)
        self.command(DISPON)

    def setAddrWindow(self, x0=0, y0=0, x1=None, y1=None):
        if x1 is None:
            x1 = self.width-1
        if y1 is None:
            y1 = self.height-1
        self.command(CASET)
        self.data(x0 >> 8)
        self.data(x0)
        self.data(x1 >> 8)
        self.data(x1)
        self.command(RASET)
        self.data(y0 >> 8)
        self.data(y0)
        self.data(y1 >> 8)
        self.data(y1)
        self.command(RAMWR)

    def display(self, image=None):
        # By default write the internal buffer to the display.
        if image is None:
            image = self.buffer
        self.setAddrWindow()
        pixelbytes = list(image_to_data(image))
        self.data(pixelbytes)

    def clear(self, color=(0,0,0)):
        width, height = self.buffer.size
        self.buffer.putdata([color]*(width*height))

    def draw(self):
        return ImageDraw.Draw(self.buffer)

    def invert(self,status):
        if (status == False):
            self.command(INVOFF)
        else:
            self.command(INVON)
	
    def setRotation(self,mode):	
        self.command(MADCTL)
        if (mode == 0x00):
            self.data(MADCTL_MY | MADCTL_MX| MADCTL_BGR)	#portrait
        elif (mode == 0x01):
            self.data(MADCTL_MV |MADCTL_ML| MADCTL_BGR)	#Landscape mode reflected 
        elif (mode == 0x02):
            self.data(MADCTL_MY | MADCTL_BGR)				#Portrait mode reflected 
        elif (mode == 0x03):
            self.data(MADCTL_MX | MADCTL_BGR)				#Portarit mode inverted and reflected
        elif (mode == 0x04):
            self.data(MADCTL_MV | MADCTL_BGR | MADCTL_MX)	#Landscape mode inverted 
        elif (mode == 0x05):
            self.data(MADCTL_ML | MADCTL_BGR)				#Portrait inverted 
        elif (mode == 0x06):
            self.data(MADCTL_MV|MADCTL_MY | MADCTL_BGR)	#Landscape mode 
        else:
            self.data(MADCTL_M8 | MADCTL_BGR)				#Landscape mode reflected and inverted

    def setGamma(self,gamma):
        self.command(NORON)
        if(gamma == 1):
            self.data(GAMMA1)
        elif(gamma == 2):
            self.data(GAMMA2)
        elif(gamma == 3):
            self.data(GAMMA3)
        else:
            self.data(GAMMA4)

    def setPartialArea(self,start,end):
        self.command(PTLON)
        self.data(start)
        self.data(start >> 8)
        self.data(end)
        self.data(end >> 8)
        self.command(PTLON)
	
    def scrollArea(self,tfa,vsa,bfa,firstline):
        self.command(SCRLAR)
        self.data(tfa)
        self.data(tfa >> 8)
        self.data(vsa)
        self.data(vsa >> 8)
        self.data(bfa)
        self.data(bfa >> 8)
        self.command(VSCSAD)
        self.data(0x00)
        self.data(firstline)
		
    def fullDisplay(self):
        self.command(NORON)

    def setColorMode(slef,mode):
        self.command(COLMOD)
        self.data(mode)
		
    def	sleep(self):
        self.command(SLEEP_IN)
        time.sleep(0.005)

    def wakeUp(self):
        self.command(SLEEP_OUT)
        time.sleep(0.120)

    def idleMode(self,onoff):
        if(onoff == 0):
            self.command(SIDLE_MODE_OFF)
        else:
            self.command(SIDLE_MODE_ON)
		
    def turnOff(self):
        self.command(DISPOFF)

    def turnOn(self):
        self.command(DISPON)
