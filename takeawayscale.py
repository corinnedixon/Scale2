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
button7 = 10
button10 = 12
button12 = 16
button14 = 18

# Button set up
GPIO.setup(button7, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(button10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(button12, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(button14, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Input pins for switch positions
cheese = 38
pepp = 40

# Button set up
GPIO.setup(cheese, GPIO.IN)
GPIO.setup(pepp, GPIO.IN)

# Class for pretop pizzas and weights
class PretopPizza:
    def __init__(self,cW,pW):
        self.cheeseWeight = cW
        self.pepWeight = pW

# Pizza dictionary for pretop weights
Pizzas = {
        "7":[0.1,0.06],
        "10":[0.22,0.15],
        "12":[0.32,0.22],
        "14":[0.44,0.3]
        }

# Function for takeaway scale
def topTakeAway(startSize,mode):
  # tare scale and initially set time of last removal
  tare()
  timeOfLastRemoval = time.time()
  
  # make sure the button or switch is not changed
  modeChange = False
  
  # set target weight from dictionary
  target = Pizzas[str(startSize)][mode]
  
  # while the target weight has not been reached by +/- 5% for 1 second
  while ((abs(scaleWeight.get()-target) > target/20) or (time.time()-timeOfLastRemoval < 1)) and not(modeChange):
    # record old weight to see if removal is still occurring
    oldWeight = scaleWeight.get()
    
    # read weight...positively if removed
    readWeight()
    
    # if the weight has changed by more than 0.01, reset time of last removal
    if(abs(scaleWeight.get()-oldWeight) > 0.01):
      timeOfLastRemoval = time.time()
    
    # update display
    updateNumbers(scaleWeight.get())
    
    # check for button press or change of mode
    modeChange = buttonPressed() or mode != getMode()
    
    time.sleep(0.001)

# Function for takeaway scale
def regTakeAway():
  # tare scale and initially set time of last removal
  tare()
  timeOfLastRemoval = time.time()
  
  # make sure the button or switch is not changed
  modeChange = False
  
  # while the scale has not been the same for 5+ seconds
  while (time.time()-timeOfLastRemoval < 5) and (not(modeChange)):
    # record old weight to see if removal is still occurring
    oldWeight = scaleWeight.get()
    
    # read weight...positively if removed
    readWeight()
    
    # if the weight has changed by more than 0.01, reset time of last removal
    if(abs(scaleWeight.get()-oldWeight) > 0.01):
      timeOfLastRemoval = time.time()
    
    # update display
    updateNumbers(scaleWeight.get())
    
    # check for button press or change of mode
    modeChange = buttonPressed() or (mode != getMode())
    
    time.sleep(0.001)

# Function to check if a button was pressed
def buttonPressed():
  press = False
  if GPIO.input(button7) == GPIO.HIGH or GPIO.input(button10) == GPIO.HIGH or GPIO.input(button12) == GPIO.HIGH or GPIO.input(button14) == GPIO.HIGH:
      press = True
  return press
  
# Function to check if a button was pressed
def getMode():
  mode = 2
  if GPIO.input(cheese) == GPIO.HIGH:
      mode = 0
  elif GPIO.input(pepp) == GPIO.HIGH:
      mode = 1
  return mode
  
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

# Get current mode for start
mode = getMode()

# Main loop
while True:
    #Run takeaway function corresponding to mode and size
    size = getSize(size)
    mode = getMode()
    if(mode == 2):
      regTakeAway()
    else:
      topTakeAway(size,mode)
