import RPi.GPIO as gpio
from time import sleep
from threading import Thread

BLUE_PIN = 21


gpio.setmode(gpio.BCM)
gpio.setup(BLUE_PIN, gpio.OUT)

gpio.output(BLUE_PIN, gpio.LOW)

p = gpio.PWM(BLUE_PIN, 50) # pin, freq (Hz)
p.start(0)

try:
    blue = LED()
    blue.fade()
    while 1:
        raw_input("Still doing things! ")

except KeyboardInterrupt:
    pass

finally:
    print "Cleaning up"
    p.stop()
    gpio.cleanup()

class LED():
    def __init__(self):
        pass

    def fade(self):
        _t = Thread(self._fade)
        _t.start()

    def _fade(self):
        while 1:
            for dc in range(0, 101, 5):
                p.ChangeDutyCycle(dc)
	        sleep(0.1)
            for dc in range(100, -1, -5):
                p.ChangeDutyCycle(dc)
                sleep(0.1)
