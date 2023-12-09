import RPi.GPIO as GPIO
import time
import os

# Set the GPIO mode and pin
GPIO.setmode(GPIO.BCM)
shutdown_pin = 23  # Change this to the GPIO pin you have connected the button to

# Set up the button as an input with pull-up resistor
GPIO.setup(shutdown_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def shutdown(channel):
    print("Button pressed! Shutting down...")
    time.sleep(1)  # Optional delay to avoid accidental triggers
    os.system("sudo killall pigpiod")
    os.system("sudo shutdown now")

# Add event detection for the button press
GPIO.add_event_detect(shutdown_pin, GPIO.FALLING, callback=shutdown, bouncetime=2000)

try:
    # Keep the script running
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    # Clean up GPIO on keyboard interrupt
    GPIO.cleanup()
