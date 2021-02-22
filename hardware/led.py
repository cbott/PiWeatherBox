import numpy as np
import RPi.GPIO as gpio
from collections import namedtuple
from threading import Thread
from time import sleep

# TODO: should we just make these 0-100 instead of 0-255?
Color = namedtuple('Color', ['Red', 'Green', 'Blue'])

def intensity_to_duty_cycle(intensity: int) -> int:
    """ Converts a 0-255 color intensity to a 0-100 duty cycle """
    return int(intensity * 100 / 255)
    # TODO: Bounds check? This is probably the wrong place for that


class RGBLED():
    # TODO: docstring and add type annotations
    def __init__(self, r_pin, g_pin, b_pin):
        # Initialize hardware
        # TODO: is there a cleaner way to do this with Tuples or maybe have named parameters?
        self.pins = [r_pin, g_pin, b_pin]
        self.pwm_channels = []
        for pin in self.pins:
            gpio.setup(pin, gpio.OUT)
            gpio.output(pin, gpio.LOW)

            pwm = gpio.PWM(pin, 75)  # pin, freq (Hz)
            pwm.start(0)
            self.pwm_channels.append(pwm)

        # Initialize current state
        self._state = "on"
        self._color = 0
        self.fade_min = 0
        self.fade_max = 100
        self.fade_step = 5
        # TODO: update time is misleading cuz it is only for const color mode not fade and such
        self.update_time = 0.01  # seconds, time that update loop takes

        # Start mainloop
        _t = Thread(target=self._loop)
        _t.start()

    def halt(self):
        """End the LED mainloop permanently"""
        self._state = "halt"

    def off(self):
        self.set(Color(0, 0, 0))

    def set(self, color: Color):
        self._color = color
        self._state = "on"

    def fade(self, color: Color, period=1):
        """Fade the LED on and off"""
        self._color = color
        self._period = period
        self._state = "fade"

    def blink(self, color: Color, period=1):
        """Blink the LED on and off"""
        self._color = color
        self._period = period
        self._state = "blink"

    def _loop(self):
        while self._state != "halt":
            # TODO: make this more threadsafe
            if self._state == "on":
                # TODO: ok yeah this enumerate is kind of gross, need named channels list
                for i, component in enumerate(self._color):
                    self.pwm_channels[i].ChangeDutyCycle(intensity_to_duty_cycle(component))
                sleep(self.update_time)

            if self._state == "fade":
                pause = 0.01  # TODO: make const
                num_steps = self._period // pause
                # TODO: this is some pro hacker moves but also has probably 3 off-by-one errors
                # TODO: could we maybe make it steps[step][component] to make the following loop nicer?
                steps = [np.concatenate((np.linspace(0,component,num_steps//2), np.linspace(component,0,num_steps//2))) for component in self._color]
                for step in range(steps):
                    for component in range(3):
                        self.pwm_channels[component].ChangeDutyCycle(intensity_to_duty_cycle(steps[component][step]))
                    sleep(pause)

            if self._state == "blink":
                # Turn on
                for i, component in enumerate(self._color):
                    self.pwm_channels[i].ChangeDutyCycle(intensity_to_duty_cycle(component))
                sleep(self._period / 2.0)
                # Turn off
                for channel in self.pwm_channels:
                    channel.ChangeDutyCycle(0)
                sleep(self._period / 2.0)

        for channel in self.pwm_channels:
            channel.stop()


class LED():
    def __init__(self, pin):
        self.pin = pin
        gpio.setup(self.pin, gpio.OUT)
        gpio.output(self.pin, gpio.LOW)
        self.pwm = gpio.PWM(self.pin, 75)  # pin, freq (Hz)
        self.pwm.start(0)

        self._state = "on"
        self._brightness = 0
        self.fade_min = 0
        self.fade_max = 100
        self.fade_step = 5
        self.update_time = 0.01  # seconds, time that update loop takes

        _t = Thread(target=self._loop)
        _t.start()

    def halt(self):
        """End the LED mainloop permanently"""
        self._state = "halt"

    def off(self):
        self.set(0)

    def set(self, brightness):
        """Set the LED to a brightness level 0 to 100"""
        self._brightness = brightness
        self._state = "on"

    def fade(self, period=1):
        """Fade the LED on and off"""
        self._period = period
        self._state = "fade"

    def blink(self, period=1, brightness=100):
        """Blink the LED on and off"""
        self._brightness = brightness
        self._period = period
        self._state = "blink"

    def _loop(self):
        while self._state != "halt":
            if self._state == "on":
                self.pwm.ChangeDutyCycle(self._brightness)
                sleep(self.update_time)

            if self._state == "fade":
                pause = self._period * self.fade_step / (2.0 * (self.fade_max - self.fade_min))
                for dc in range(self.fade_min, self.fade_max + 1, self.fade_step):
                    self.pwm.ChangeDutyCycle(dc)
                    sleep(pause)
                for dc in range(self.fade_max, self.fade_min - 1, -self.fade_step):
                    self.pwm.ChangeDutyCycle(dc)
                    sleep(pause)

            if self._state == "blink":
                self.pwm.ChangeDutyCycle(self._brightness)
                sleep(self._period / 2.0)
                self.pwm.ChangeDutyCycle(0)
                sleep(self._period / 2.0)

        self.pwm.stop()


if __name__ == "__main__":
    # TODO: Update to use RGBLED and delete LED
    PIN = 21
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
        print("Cleaning up")
        blue.halt()
        gpio.cleanup()
