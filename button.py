import RPi.GPIO as gpio
import time

BUTTON_PIN = 26
gpio.setmode(gpio.BCM)

class TriggerButton:
    """ A button that triggers events when pressed or held for a length of time """
    def __init__(self, pin, press_callback = lambda:None, hold_callback = lambda:None, hold_time = 1):
        self.pin = pin
        self.press_callback = press_callback
        self.hold_callback = hold_callback
        self.hold_time = hold_time

        gpio.setup(self.pin, gpio.IN)
        gpio.add_event_detect(self.pin, gpio.BOTH, callback = self._on_event, bouncetime = 100)
        
        self._presstime = time.time()
        self._active = False

        _hold_monitor = Thread(target = self._loop)
        _hold_monitor.daemon = True
        _hold_monitor.start()

    def get_pressed(self):
        # Returns whether or not the button is currently pressed
        return gpio.input(self.pin)

    def get_held(self):
        # Returns how long the button has been pressed for
        # Or how long it has been unpressed for (indicated as a negative value)
        if self._active:
            return time.time() - self._presstime
        else:
            return self._presstime - time.time()

    def _on_event(self, channel):
        if self.get_pressed():
            print "Button Pressed"
            self._active = True
            self._presstime = time.time()
            self.press_callback()
        else:
            print "Button Released"
            self._active = False
            self._presstime = time.time()

    def _loop(self):
        if(self.get_held() > self.hold_time):
            self.hold_callback()
        time.sleep(0.01)

class Button:
    def __init__(self, pin):
        self.pin = pin
        gpio.setup(self.pin, gpio.IN)

    def get_pressed(self):
        # Returns whether or not the button is currently pressed
        return gpio.input(self.pin)

def hcb():
    return 1/0

try:
    btn = TriggerButton(BUTTON_PIN, hold_callback = hcb, hold_time = 3)

    print "Doing Stuff"
    while 1:
        time.sleep(1)
    print "Shutting Down..."
except KeyboardInterrupt:
    print "Keyboard Interrupt. Shutting Down..."

finally:
    gpio.cleanup()
