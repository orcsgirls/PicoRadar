import time
import board
import digitalio

# Notes on buttons
# (1) Button A (GP15) cannot be used due to Pico limitations
# (2) the value isTrue for NOT pressed and False for pressed 

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

while True:
    print('Button B', button_b.value)
    print('Joy up/down/ left/ right ', joy_up.value, joy_down.value, joy_left.value, joy_right.value)
    time.sleep(0.5)