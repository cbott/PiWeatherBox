import RPi.GPIO as gpio
import time

BUTTON_PIN = 20
gpio.setmode(gpio.BCM)
gpio.setup(BUTTON_PIN, gpio.IN)

def on_btn_event(channel):
    global presstime, shutdown
    if gpio.input(BUTTON_PIN):
        print "Button Pressed"
	presstime = time.time()
    else:
        print "Button Released!"
        elapsed = time.time() - presstime
        if elapsed > 3:
            shutdown = True

try:
    shutdown = False
    presstime = time.time()

    gpio.add_event_detect(BUTTON_PIN, gpio.BOTH, callback = on_btn_event, bouncetime = 100)

    print "Doing Stuff"
    while not shutdown:
        time.sleep(0.1)
    print "Shutting Down..."
except KeyboardInterrupt:
    print "Keyboard Interrupt. Shutting Down..."

finally:
    gpio.cleanup()
