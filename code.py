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
WATERING_LIMIT = 30


#Functions

#Return moist level in %
def get_moist_level():
    voltage = (moist_sensor.value * 3.3) / 65536
    percentage = 100 - (voltage / 3.3) * 100   
    return round(percentage)

def blink_led(duration):
    for i in range(duration):
        led.value = True
        time.sleep(0.5)
        led.value = False
        time.sleep(0.5)

def display_moist_level():
    text_area_upper.x = 0
    text_area_upper.y = 5
    text = "Moist level: " + str(get_moist_level()) + " %"
    text_area_upper.text = text
    text_area_lower.text = "Lower limit: " + str(WATERING_LIMIT) + " %"
    display.refresh()

def scroll_text(display, text_area_upper, text):
    text_area_upper.x = display.width
    text_area_upper.y = 5
    text_area_upper.text = text
    while text_area_upper.x >= (-3.5 * len(text) - display.width - 5):
        text_area_upper.x -= 3
        time.sleep(1 / 60)
        display.refresh()

def present_joke():
    global current_joke
    
    joke = jokes[current_joke].split(",")
    question = joke[0].strip()[1:].replace('"', '')
    answer = joke[1].strip()[:-1].replace('"', '')
       
    display.show(splash)
    
    scroll_text(display, text_area_upper, question)
    time.sleep(1)
    scroll_text(display, text_area_upper, answer)
    
    display.show(None)
    
    current_joke = (current_joke + 1) % len(jokes)
    
def flash_text(text):
    display.show(splash)
    text_area_upper.x = 35
    text_area_upper.y = 12
    text_area_upper.scale = 3
    for i in range(3):
        text_area_upper.text = text
        time.sleep(0.3)
        text_area_upper.text = ""
        time.sleep(0.3)
  
    text_area_upper.scale = 1 
    
    display.show(None)

def clear_text():
    text_area_lower.text = ""
    text_area_upper.text = ""

#Setup
displayio.release_displays()
i2c = busio.I2C(scl=display_scl, sda=display_sda)
display_bus = displayio.I2CDisplay(i2c, device_address=DISPLAY_ADR)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=WIDTH, height=HEIGHT, rotation=180)
splash = displayio.Group()
display.show(splash)

current_moist_level = str(get_moist_level())
text_area_upper = label.Label(
    terminalio.FONT, text=current_moist_level, color=0xFFFFFF, x=0, y=5, scale=1
)
splash.append(text_area_upper)

text_area_lower = label.Label(
    terminalio.FONT, text="", color=0xFFFFFF, x=0, y=18
)
splash.append(text_area_lower)

#display.refresh()

# Load the jokes from the text file
jokes = []
with open("jokes.txt", "r") as file:
    jokes = file.read().splitlines()

current_joke = 0
#Main
while True:
    display.show(splash)
    moist_level = 0
    while moist_level < WATERING_LIMIT:
        for i in range(5):
            display_moist_level()
            moist_level = get_moist_level()
            if moist_level < WATERING_LIMIT:
                pump.value = True
                led.value = True
                
            else:
                pump.value = False
                led.value = False
            time.sleep(1)
            
    clear_text()       
    display.show(None)
    
    present_joke()
    flash_text("LOL!")
    clear_text()
    
    
    
