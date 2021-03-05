import numpy as np
import RPi.GPIO as gpio
from collections import namedtuple
from threading import Thread
from time import sleep
from typing import Iterable

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
        self._state = 'on'  # TODO: Enum this maybe?
        self._color = Color(0, 0, 0)
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

    def _write_all_pwm_channels(self, color: Iterable) -> None:
        """ Helper function to write the R, G, and B PWM channels for the LED given a Color tuple or other length 3 iterable """
        assert len(color) == 3
        for i in range(3):
            self.pwm_channels[i].ChangeDutyCycle(intensity_to_duty_cycle(color[i]))

    def _loop(self):
        while self._state != 'halt':
            # TODO: make this more threadsafe
            if self._state == 'on':
                self._write_all_pwm_channels(self._color)
                sleep(self.update_time)

            if self._state == 'fade':
                pause = 0.01  # TODO: make const
                num_steps = int(self._period / pause / 2)  # number of steps before reversing direction
                # TODO: this is some SUPER pro hacker moves but also has probably 3 off-by-one errors
                # Create a 2D array of values, with a column for each color component and a row for each step of the fade
                up_steps = np.linspace((0, 0, 0), self._color, num_steps)
                steps = np.concatenate((up_steps, up_steps[::-1]))
                for step in steps:
                    self._write_all_pwm_channels(step)
                    sleep(pause)

            if self._state == 'blink':
                # Turn on
                self._write_all_pwm_channels(self._color)
                sleep(self._period / 2.0)
                # Turn off
                self._write_all_pwm_channels((0, 0, 0))
                sleep(self._period / 2.0)

        for channel in self.pwm_channels:
            channel.stop()


if __name__ == "__main__":
    # TODO: Update to use RGBLED and delete LED
    RED_PIN = 16
    GREEN_PIN = 20
    BLUE_PIN = 21
    gpio.setmode(gpio.BCM)

    try:
        led = RGBLED(RED_PIN, GREEN_PIN, BLUE_PIN)

        colors = [Color(255, 0, 0),
                  Color(0, 255, 0),
                  Color(0, 0, 255),
                  Color(255, 128, 0)]
        modes = [led.set, led.fade, led.blink]

        while 1:
            for mode in modes:
                for color in colors:
                    mode(color)
                    sleep(3)

    finally:
        print("Cleaning up")
        led.halt()
        gpio.cleanup()
