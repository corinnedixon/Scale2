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
GPIO.setwarnings(False)

# LED matrix setup
sr = spi(port=0, device=0, gpio=noop(), cs_high=True)
device = max7219(sr, cascaded=4, block_orientation=-90)

# Input pins for each button
button7 = 11
button10 = 12
button12 = 13
button14 = 15

# Button set up
GPIO.setup(button7, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(button10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(button12, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(button14, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Pizza dictionary with cheese weights
Pizzas = {"7":0.1, "10":0.22, "12":0.32, "14":0.44}

# Function for takeaway scale
def takeAway(startSize):
  # tare scale and initially set time of last removal
  tare()
  timeOfLastRemoval = time.time()
  
  # same size is initially true
  sameSize = True
  
  # set target weight from dictionary
  target = Pizzas[str(startSize)]
  
  # while the target weight has not been reached by +/- 5% for 1 second
  while (abs(scaleWeight.get()-target) > target/20) or (time.time()-timeOfLastRemoval < 1) and sameSize:
    # record old weight to see if removal is still occurring
    oldWeight = scaleWeight.get()
    
    # read weight...positively if removed
    readWeight()
    
    # if the weight has changed by more than 0.01, reset time of last removal
    if(abs(scaleWeight.get()-oldWeight) > 0.01):
      timeOfLastRemoval = time.time()
    
    # update display
    updateNumbers(scaleWeight.get())
    
    # check for more button press
    currentSize = getSize(startSize)
    if currentSize != startSize:
      sameSize = False
    
    time.sleep(0.001)

# Funciton for size input from buttons
def getSize(currentSize):
    size = currentSize
    if GPIO.input(button7) == GPIO.HIGH:
      size = 7
    elif GPIO.input(button10) == GPIO.HIGH:
      size = 10
    elif GPIO.input(button12) == GPIO.HIGH:
      size = 12
    elif GPIO.input(button14) == GPIO.HIGH:
      size = 14
    return size

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
    
# Tare scale before start
serial_open()
tare()

# Default size set to 14
size = 14

# Main loop
while True:
    #Run takeaway function with collected size weight
    size = getSize(size)
    print(size)
    takeAway(size)
