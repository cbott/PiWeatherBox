import RPi.GPIO as gpio
from time import sleep

gpio.setmode(gpio.BCM)
gpio.setup(21, gpio.IN)

try:
	while 1:
		print(gpio.input(21))
		sleep(0.1)
except KeyboardInterrupt:
	gpio.cleanup()
