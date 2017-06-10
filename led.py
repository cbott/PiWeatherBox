import RPi.GPIO as gpio
from threading import Thread
from time import sleep

class LED():
    def __init__(self, pin):
        self.pin = pin
        gpio.setup(self.pin, gpio.OUT)
        gpio.output(self.pin, gpio.LOW)
        self.pwm = gpio.PWM(self.pin, 75) # pin, freq (Hz)
        self.pwm.start(0)

        self._state = "on"
        self._brightness = 0
        self.fade_min = 0
        self.fade_max = 100
        self.fade_step = 5


        _t = Thread(target = self._loop)
        _t.daemon = True
        _t.start()

    def halt(self):
        self._state = "done"

    def off(self):
        self.set(0)

    def set(self, brightness):
        """ set the LED to a brightness level 0 to 100 """
        self._brightness = brightness
        self._state = "on"

    def fade(self, period = 1):
        """ Fade the LED on and off """
        self._period = period
        self._state = "fade"

    def blink(self, period = 1):
        """ Blink the LED on and off """
        self._period = period
        self._state = "blink"

    def _loop(self):
        while self._state != "done":
            if self._state == "on":
                self.pwm.ChangeDutyCycle(self._brightness)
                sleep(0.1)

            if self._state == "fade":
                pause = self._period * self.fade_step / (2.0 * (self.fade_max - self.fade_min))
                for dc in range(self.fade_min, self.fade_max+1, self.fade_step):
                    self.pwm.ChangeDutyCycle(dc)
                    sleep(pause)
                for dc in range(self.fade_max, self.fade_min-1, -self.fade_step):
                    self.pwm.ChangeDutyCycle(dc)
                    sleep(pause)

            if self._state == "blink":
                self.pwm.ChangeDutyCycle(100)
                sleep(self._period / 2.0)
                self.pwm.ChangeDutyCycle(0)
                sleep(self._period / 2.0)

        self.pwm.stop()

if __name__ == "__main__":
    PIN = 13
    gpio.setmode(gpio.BCM)
    try:
        blue = LED(PIN)
        while 1:
            blue.fade()
            sleep(5)
            blue.blink()
            sleep(5)
            blue.set(50)
            sleep(5)

    except KeyboardInterrupt:
        pass

    finally:
        print "Cleaning up"
        gpio.cleanup()
