import time
import math
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
# Radar Version 2
#
# Rotate and display distance as number on the screen.
# Created using cut&paste from examples
#
# New features
# - Start/Stop   Button B
# - Joy up/down  cm / in display
#---------------------------------------------------------------------------------

# PIN setup - change to match your setup
TRIGGER_PIN = board.GP0   # Ultrasonic sensor
ECHO_PIN    = board.GP1
SERVO_PIN   = board.GP19  # Servo
BUZZER_PIN  = board.GP21  # Buzzer (fixed on the board)

# PIN setup for buttons 
BUTTON_B    = board.GP17  # Button B on display
JOY_UP      = board.GP2   # Joystick up
JOY_DOWN    = board.GP18  # Joystick down
JOY_LEFT    = board.GP16  # Joystick left
JOY_RIGHT   = board.GP20  # Joystick right

def make_button(pin):
    button = digitalio.DigitalInOut(pin)
    button.switch_to_input(pull=digitalio.Pull.UP)
    return button
    
button_b  = make_button(BUTTON_B)
joy_up    = make_button(JOY_UP)
joy_down  = make_button(JOY_DOWN)
joy_left  = make_button(JOY_LEFT)
joy_right = make_button(JOY_RIGHT)

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
label=Label(terminalio.FONT, color=0xFFFFFF, scale=3, text="ORCSGirls", 
            anchor_point=(0.5,0.5), anchored_position=(display.width//2,display.height//2))
group.append(label)   # Add it to the screen

# Make sonar sensor object
sonar = adafruit_hcsr04.HCSR04(trigger_pin=TRIGGER_PIN, echo_pin=ECHO_PIN)
sonar_scale = 1.0  # Length scale for radar display

# Create a servo object, my_servo.
pwm = pwmio.PWMOut(SERVO_PIN, duty_cycle=2 ** 15, frequency=50)
my_servo = servo.Servo(pwm)

# Radar center
center_x, center_y = display.width//2, display.height

# Scanning start and end angle and step size
START_ANGLE = 0
END_ANGLE   = 180
STEP_ANGLE  = 5

#---------------------------------------------------------------------------------
def next_angle(angle,step):
    if angle + step > END_ANGLE:
        return angle-step, -step
    elif angle + step < START_ANGLE:
        return angle-step, -step
    else:
        return angle + step, step

#---------------------------------------------------------------------------------
def get_distance():
    try:
        return sonar.distance
    except RuntimeError:
        return 0
        
#---------------------------------------------------------------------------------
def draw_static_radar():
    """Draws static radar grid lines."""
    static_group = displayio.Group()
    for r in range(40, display.height, 40):
        static_group.append(Circle(center_x, center_y, r, outline=0xFFFF00))
        static_group.append(Label(terminalio.FONT, color=0xFFFF00, scale=2, text=str(int(r/sonar_scale)),
                                 anchor_point=(0.5,0.0), anchored_position=(center_x,center_y-r)))

    return static_group

#---------------------------------------------------------------------------------
def draw_radar(angle, distance, sweep_group):
    """Draws the radar scan result on the ST7789 display."""
    print (f"Angle: {angle} - Distance: {distance} cm")
    # Convert polar to Cartesian coordinates
    radians = math.radians(angle)
    scaled_distance = min(sonar_scale*distance, display.width/2)
    target_x = int(center_x + scaled_distance * math.cos(radians))
    target_y = int(center_y - scaled_distance * math.sin(radians))

    # Draw sweeping line
    sweep_x = int(center_x + display.width/2 * math.cos(radians))
    sweep_y = int(center_y - display.width/2 * math.sin(radians))
    sweep_group.append(Line(center_x, center_y, target_x, target_y, color=0x00FF00))
    sweep_group.append(Line(target_x, target_y, sweep_x, sweep_y, color=0xFF0000))
    
    
# Draw the grid
label.text=""
static_group = draw_static_radar()
group.append(static_group)
sweep_group = displayio.Group()
group.append(sweep_group)

#---------------------------------------------------------------------------------
# Main sweeping loop
# Note we changed how we change angle from a list to calculating it.
# This makes stopping and continuing easier :)
#---------------------------------------------------------------------------------

running = True
angle = START_ANGLE
step = STEP_ANGLE

while True:
    if running:
        # To save display memory, we remove the lines after every sweep
        if(angle==0 or angle==180):
            group.remove(sweep_group)
            sweep_group = displayio.Group()
            group.append(sweep_group)
            
        my_servo.angle = angle                  # Rotate to the angle
        distance = get_distance()               # Measure distance
        draw_radar(angle, distance, sweep_group)
        angle, step = next_angle(angle, step)   # Getting the next angle 
        time.sleep(0.5)                         # Wait a little

    # Check buttons
    if not button_b.value:
        running = not running
        time.sleep(0.5)
        
    time.sleep(0.05)