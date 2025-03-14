import time
import board
import adafruit_hcsr04

# Pins for the ultrasonic sensor. Change to match your setup
TRIGGER_PIN = board.GP0
ECHO_PIN = board.GP1

# Make sonar sensor object
sonar = adafruit_hcsr04.HCSR04(trigger_pin=TRIGGER_PIN, echo_pin=ECHO_PIN)

print("startplot:","distance")   # This line will allow plotting 

# Loop to measure
while True:
    try:
        print(sonar.distance)
    except RuntimeError:
        print("Retrying!")
    time.sleep(0.2)

