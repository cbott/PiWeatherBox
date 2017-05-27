import RPi.GPIO as gpio
from time import sleep

BLUE_PIN = 21


gpio.setmode(gpio.BCM)
gpio.setup(BLUE_PIN, gpio.OUT)

gpio.output(BLUE_PIN, gpio.LOW)

p = gpio.PWM(BLUE_PIN, 50) # pin, freq (Hz)
p.start(0)

try:
    while 1:
        for dc in range(0, 101, 5):
            p.ChangeDutyCycle(dc)
            sleep(0.1)
        for dc in range(100, -1, -5):
            p.ChangeDutyCycle(dc)
            sleep(0.1)

except KeyboardInterrupt:
    pass

finally:
    print "Cleaning up"
    p.stop()
    gpio.cleanup()
