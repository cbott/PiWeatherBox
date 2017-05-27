import RPi.GPIO as gpio
import time

BUTTON_PIN = 20
gpio.setmode(gpio.BCM)
gpio.setup(BUTTON_PIN, gpio.IN)

def on_press(channel):
    print "Pressed!"

def on_release(channel):
    print "Released!"

try:
    shutdown = false
    presstime = time.time()

    gpio.add_event_detect(BUTTON_PIN, gpio.RISING, callback = on_press, bouncetime = 100)
    gpio.add_event_detect(BUTTON_PIN, gpio.FALLING, callback = on_release, bouncetime = 100)

    while not shutdown:
        print "Doing Stuff"
        time.sleep(1)

except KeyboardInterrupt:
    print "Keyboard Interrupt. Shutting Down..."

finally:
    gpio.cleanup()
