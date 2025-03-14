# Various imports
import board
import busio
import digitalio
import pwmio
import time
import math
import displayio
import adafruit_st7789
import terminalio
import adafruit_hcsr04
from adafruit_motor import servo
from fourwire import FourWire
from adafruit_display_shapes.line import Line
from adafruit_display_shapes.circle import Circle
from adafruit_display_text.label import Label

# Initialize SPI display
displayio.release_displays()
spi = busio.SPI(clock=board.GP10, MOSI=board.GP11, MISO=None)
tft_cs = board.GP9
tft_dc = board.GP8
tft_rst = board.GP12
display_bus = FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_rst)
display = adafruit_st7789.ST7789(display_bus, rotation=270,
                                 width=240, height=135, rowstart=40, colstart=53)

# Display stuff
group = displayio.Group()
display.root_group = group  # Updated to use root_group

# Display welcome
center_x, center_y = display.width//2, display.height//2
group.append(Label(terminalio.FONT, color=0xFFFFFF, scale=2, text="ORCSGirls",
                   anchor_point=(0.5,0.5), anchored_position=(center_x,center_y)))

# Do nothing
while True:
   time.sleep(0.01)
   pass
