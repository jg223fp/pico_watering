import board
import busio
import displayio
import terminalio
import digitalio
import time
import microcontroller
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
WATERING_LIMIT = 30  # in %


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

def display_moist_level(moist):
    text_area_upper.x = 0
    text_area_upper.y = 5
    text = "Moist level: " + str(moist) + " %"
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
    
    joke = jokes[current_joke].split(";")
    question = joke[0].strip()[1:].replace('"', '').replace('\\','')
    answer = joke[1].strip()[:-1].replace('"', '').replace('\\','')
       
    display.show(splash)
    
    scroll_text(display, text_area_upper, question)
    flash_text("???")
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
    

def clear_text():
    text_area_lower.text = ""
    text_area_upper.text = ""
    
def cool_effect(add_Text):
    width = 1
    height = 1

    # Calculate the initial positions
    x_left = 0
    x_right = display.width - width

    steps = WIDTH//4 + 3
    for step in range(steps):
        inner_bitmap_left = displayio.Bitmap(width, height, 1)
        inner_palette = displayio.Palette(1)
        inner_palette[0] = 0xFFFFF
        inner_sprite_left = displayio.TileGrid(inner_bitmap_left, pixel_shader=inner_palette, x=x_left, y=display.height - height)
        inner_sprite_right = displayio.TileGrid(inner_bitmap_left, pixel_shader=inner_palette, x=x_right, y=display.height - height)

        splash.append(inner_sprite_left)
        splash.append(inner_sprite_right)

        width += 2
        height += 1

        x_left = max(0, x_left - 1)
        x_right = min(display.width - width, x_right + 1)

        time.sleep(0.01)
    
    # Add text while squares covers the screen
    if add_Text:
        display_moist_level(get_moist_level())
    else: 
        clear_text()
        
    for step in range(steps):
        splash.pop()
        splash.pop()
        time.sleep(0.01)

#Setup
displayio.release_displays()
i2c = busio.I2C(scl=display_scl, sda=display_sda)
display_bus = displayio.I2CDisplay(i2c, device_address=DISPLAY_ADR)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=WIDTH, height=HEIGHT, rotation=180)
splash = displayio.Group()
display.show(splash)

current_moist_level = str(get_moist_level())
text_area_upper = label.Label(
    terminalio.FONT, text="BOOT", color=0xFFFFFF, x=0, y=5, scale=1
)
splash.append(text_area_upper)

text_area_lower = label.Label(
    terminalio.FONT, text="BOOT", color=0xFFFFFF, x=0, y=18
)
splash.append(text_area_lower)

# Load the jokes from the text file
jokes = []
last_joke_row = 0
with open("jokes.txt", "r") as file:
    jokes = file.read().splitlines()
    for line in file:
        last_joke_row += 1
    file.close()

current_joke = 0
#Main
while True:
    display.show(splash)
    
    moist_level = 0
    while moist_level < WATERING_LIMIT:
        for i in range(5):
            moist_level = get_moist_level()
            display_moist_level(moist_level)          
            
            if moist_level < WATERING_LIMIT:
                pump.value = True     
            else:
                pump.value = False
            time.sleep(1)
            
    #clear_text()       
    #display.show(None)
    cool_effect(False)
    
    present_joke()
    flash_text("LOL!")
    cool_effect(True)
    
    if current_joke > last_joke_row:
       microcontroller.reset()
    
    
    