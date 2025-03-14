import time
import board
import pwmio
import busio
import digitalio
import displayio
import terminalio
import adafruit_st7789
import adafruit_hcsr04
from fourwire import FourWire
from adafruit_motor import servo
from adafruit_motor import servo
from adafruit_display_shapes.line import Line
from adafruit_display_shapes.circle import Circle
from adafruit_display_text.label import Label

#---------------------------------------------------------------------------------
# Radar Version 1.5
#
# Rotate and display distance as number on the screen.
# Created using cut&paste from examples
#
# Added color change for distance
# Added buzzer for objects too close
#---------------------------------------------------------------------------------

# PIN setup - change to match your setup
TRIGGER_PIN = board.GP0   # Ultrasonic sensor
ECHO_PIN    = board.GP1
SERVO_PIN   = board.GP19  # Servo
BUZZER_PIN  = board.GP21  # Buzzer (fixed on the board)

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

# Make label and put it in the middle
center_x, center_y = display.width//2, display.height//2
label=Label(terminalio.FONT, color=0xFFFFFF, scale=3, text="ORCSGirls", 
            anchor_point=(0.5,0.5), anchored_position=(center_x,center_y))
group.append(label)   # Add it to the screen

# Make sonar sensor object
sonar = adafruit_hcsr04.HCSR04(trigger_pin=TRIGGER_PIN, echo_pin=ECHO_PIN)

# Create a servo object, my_servo.
pwm = pwmio.PWMOut(SERVO_PIN, duty_cycle=2 ** 15, frequency=50)
my_servo = servo.Servo(pwm)

# Buzzer

# Scanning start and end angle and step size
START_ANGLE = 0
END_ANGLE   = 180
STEP_ANGLE  = 5

# Make the list of angles - this is easier than running two loops
angles =  list(range(START_ANGLE, END_ANGLE, STEP_ANGLE))
angles += list(range(END_ANGLE, START_ANGLE, -STEP_ANGLE))

# Buzzer
buzzer = digitalio.DigitalInOut(BUZZER_PIN)
buzzer.direction = digitalio.Direction.OUTPUT

#---------------------------------------------------------------------------------
def get_distance():
    try:
        return sonar.distance
    except RuntimeError:
        return 0
        
#---------------------------------------------------------------------------------
def display_distance(distance):
    """ Displays the distance on the LCD screen """
    print(distance)  # For console and plot
    
    buzzer.value = False
    if distance > 0:
        if distance < 10:
            label.color=0xFF0000
            buzzer.value = True
        elif distance < 20:
            label.color=0xFFFF00
        else:
            label.color=0x00FF00
        label.text=f"{distance:.2f} cm"
    else:
        label.color=0xFF0000
        label.text="Read error"
    
#---------------------------------------------------------------------------------
# Main sweeping loop
#---------------------------------------------------------------------------------

while True:
    # Loop over angles
    for angle in angles:
        my_servo.angle = angle      # Rotate to the angle
        distance = get_distance()   # Measure distance
        display_distance(distance)  # Put it on the screen - using our routine
        time.sleep(0.5)             # Wait a little
