import sys
import time
import serial
import datetime
import RPi.GPIO as GPIO
from luma.core.legacy import text
from luma.core.render import canvas
from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.legacy.font import proportional, LCD_FONT

# Board set up
GPIO.setmode(GPIO.BOARD)

# LED matrix setup
sr = spi(port=0, device=0, gpio=noop(), cs_high=True)
device = max7219(sr, cascaded=4, block_orientation=-90)

# Function for takeaway scale
def takeAway():
  # tare scale and initially set time of last removal
  tare()
  timeOfLastRemoval = time.time()
  
  # while the scale has not been the same for 5+ seconds
  while time.time()-timeOfLastRemoval < 5:
    # record old weight to see if removal is still occurring
    oldWeight = scaleWeight.get()
    
    # read weight...positively if removed
    readWeight()
    
    # if the weight has changed by more than 0.01, reset time of last removal
    if(abs(scaleWeight.get()-oldWeight) > 0.01):
      timeOfLastRemoval = time.time()
    
    # update display
    updateNumbers(scaleWeight.get())
    
    time.sleep(0.001)

# Function for numeric display
def updateNumbers(lbs):
  msg = str(lbs)
  with canvas(device) as draw:
    text(draw, (0, 0), msg, fill="white", font=proportional(LCD_FONT))

# Mutable double class for keeping track of weight
class MutableDouble(float):
    def __init__(self, val = 0):
        self.num = val
    def set(self, val):
        self.num = val
    def get(self):
      return self.num
        
# Scale functions from saucer.py
ser = serial.Serial()
ser.port = "/dev/ttyUSB0"
ser.baudrate = 9600
scaleWeight = MutableDouble()

# Updates the weight on the scale screen
def readWeight():
    if ser.isOpen():
        try:
            if ser.in_waiting >= 9:
                b = ser.read_all()
                b2 = b.decode("utf-8")
                if b2[0] == "W":
                    if b2[b2.find(":") + 1] == "-":
                        fac = -1
                    else:
                        fac = 1

                    b3 = b2[b2.find(":") + 2:b2.find(":") + 9].strip()

                    try:
                        x = round(float(b3) * -fac * 2.20462,2)
                        if x==0:
                          scaleWeight.set(0.0)
                        else:
                          scaleWeight.set(x)
                    except ValueError:
                        pass
            else:
                pass
        except serial.serialutil.SerialException:
            serial_open()
        except UnicodeDecodeError:
          pass
    else:
        serial_open()
    time.sleep(.01)

# Opens the serial port and starts recieving data from scale
def serial_open():
    try:
        ser.open()
        ser.flush()
    except serial.serialutil.SerialException:
       pass

# Tares the scale to zero when you press the button
def tare():
    ser.write(b'TK\n')
    
#Tare scale before start
serial_open()
tare()

# Main loop
while True:
    #Run takeaway function
    takeAway()
