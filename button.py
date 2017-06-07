import RPi.GPIO as gpio
import time

BUTTON_PIN = 26
gpio.setmode(gpio.BCM)

class Button:
    def __init__(self, pin):
        self.pin = pin
        gpio.setup(self.pin, gpio.IN)
        gpio.add_event_detect(self.pin, gpio.BOTH, callback = self._on_event, bouncetime = 100)
        
        self._presstime = time.time()
        self._active = False

    def get_pressed(self):
        # Returns whether or not the button is currently pressed
        return gpio.input(self.pin)

    def hold_time(self):
        # Returns how long the button has been pressed for, or 0 if it is not pressed
        if not self._active:
            return 0
        else:
            return time.time() - self._presstime

    def _on_event(self, channel):
        if self.get_pressed():
            print "Button Pressed"
            self._active = True
            self._presstime = time.time()
        else:
            print "Button Released"
            self._active = False

try:
    btn = Button(BUTTON_PIN)

    print "Doing Stuff"
    while btn.hold_time() < 3:
        time.sleep(0.1)
    print "Shutting Down..."
except KeyboardInterrupt:
    print "Keyboard Interrupt. Shutting Down..."

finally:
    gpio.cleanup()
