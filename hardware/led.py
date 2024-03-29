# led.py
import itertools
import numpy as np
import RPi.GPIO as gpio

from collections import namedtuple
from enum import Enum, auto
from threading import Thread
from time import sleep
from typing import Iterable

Color = namedtuple('Color', ['Red', 'Green', 'Blue'])


def intensity_to_duty_cycle(intensity: float) -> float:
    """ Converts a 0-255 color intensity to a 0-100 duty cycle """
    return intensity * 100.0 / 255.0


class RGBLED():
    """
    Hardware class to control an RGB LED from a Raspberry Pi
    """
    class State(Enum):
        HALT = auto()
        ON = auto()
        FADE = auto()
        BLINK = auto()

    def __init__(self, r_pin: int, g_pin: int, b_pin: int):
        # Initialize hardware
        self.pins = [r_pin, g_pin, b_pin]
        self.pwm_channels = []
        for pin in self.pins:
            gpio.setup(pin, gpio.OUT)
            gpio.output(pin, gpio.LOW)
            pwm = gpio.PWM(pin, 75)  # pin, freq (Hz)
            pwm.start(0)
            self.pwm_channels.append(pwm)

        # Initialize current state
        self._state = self.State.ON
        self._color = Color(0, 0, 0)
        self._period = 1
        self.update_time = 0.01  # seconds, time that update loop takes

        # Start mainloop
        _t = Thread(target=self._loop)
        _t.start()

    def halt(self):
        """End the LED mainloop permanently"""
        self._state = self.State.HALT

    def off(self):
        self.set(Color(0, 0, 0))

    def set(self, color: Color):
        self._color = color
        self._state = self.State.ON

    def fade(self, color: Color, period=1):
        """Fade the LED on and off"""
        self._color = color
        self._period = period
        self._state = self.State.FADE

    def blink(self, color: Color, period=1):
        """Blink the LED on and off"""
        self._color = color
        self._period = period
        self._state = self.State.BLINK

    def _write_pwm_channel(self, channel: gpio.PWM, duty_cycle: float):
        """ Helper function to set duty cycle of a PWM channel, with bounds checking """
        if duty_cycle < 0 or duty_cycle > 100:
            raise ValueError(f'Duty cycle {duty_cycle} does not not fall in the range [0, 100]')
        channel.ChangeDutyCycle(duty_cycle)

    def _write_color(self, color: Iterable[float]) -> None:
        """ Helper function to write the R, G, and B PWM channels for the LED given a Color tuple or other length 3 iterable """
        assert len(color) == 3
        for i in range(3):
            self._write_pwm_channel(self.pwm_channels[i], intensity_to_duty_cycle(color[i]))

    def _loop(self):
        """ LED mainloop, executed in thread """
        # TODO: restructure to avoid long sleep times
        try:
            prev_state = self._state
            prev_color = self._color
            prev_period = self._period
            infinite_color_plan = itertools.cycle([prev_color])

            while self._state is not self.State.HALT:
                # hold values for some small amount of thread safety
                state = self._state
                period = self._period
                color = self._color

                if (state != prev_state) or (color != prev_color) or (period != prev_period):
                    # State update has occurred, reset the color plan generator
                    if state is self.State.ON:
                        color_plan = [color]

                    elif state is self.State.FADE:
                        num_steps = int(period / self.update_time / 2.0)  # number of steps before reversing direction
                        # This is some super pro-hacker moves
                        # Create a 2D array of values, with a column for each color component and a row for each step of the fade
                        up_steps = np.linspace((0, 0, 0), color, num_steps)
                        color_plan = np.concatenate((up_steps, up_steps[::-1]))

                    elif state is self.State.BLINK:
                        n_repeats = int(period / self.update_time / 2.0)
                        color_plan = itertools.chain(
                            itertools.repeat(color, n_repeats),
                            itertools.repeat((0, 0, 0), n_repeats)
                        )

                    else:
                        break

                    infinite_color_plan = itertools.cycle(color_plan)

                self._write_color(next(infinite_color_plan))
                prev_state = state
                prev_color = color
                prev_period = period
                sleep(self.update_time)

        finally:
            for channel in self.pwm_channels:
                channel.stop()


if __name__ == "__main__":
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
