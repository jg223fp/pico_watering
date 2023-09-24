import board
import busio
import displayio
import terminalio
import digitalio
import time
import adafruit_displayio_ssd1306
from adafruit_display_text import label
from analogio import AnalogIn


#Pinout
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
pump = digitalio.DigitalInOut(board.GP22)
pump.direction = digitalio.Direction.OUTPUT
moist_sensor = AnalogIn(board.A0)
display_sda = board.GP6
display_scl = board.GP7

#Display conf
DISPLAY_ADR = 0x3C
WIDTH = 128
HEIGHT = 32
BORDER = 1

#Moistlevels
# high = 0 v
# low = 3.3

#Functions

#Return moist level in %
def get_moist_level():
    voltage = (moist_sensor.value * 3.3) / 65536
    percentage = 100 - (voltage / 3.3) * 100   
    return round(percentage)

def pump_water():
    pump.value = True
    time.sleep(2) 
    pump.value = False

def blink_led(duration):
    for i in range(duration):
        led.value = True
        time.sleep(0.5)
        led.value = False
        time.sleep(0.5)

def display_moist_level():
    text = "Moist level: " + str(get_moist_level()) + " %"
    text_area.text = text
    display.refresh()

#Setup
displayio.release_displays()
i2c = busio.I2C(scl=display_scl, sda=display_sda)
display_bus = displayio.I2CDisplay(i2c, device_address=DISPLAY_ADR)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=WIDTH, height=HEIGHT, rotation=180)
splash = displayio.Group()
display.show(splash)

current_moist_level = str(get_moist_level())
text_area = label.Label(
    terminalio.FONT, text=current_moist_level, color=0xFFFFFF, x=0, y=5
)
splash.append(text_area)
display.refresh()



#Main
while True:
    display_moist_level()
    time.sleep(1)
