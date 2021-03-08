import logging
import numpy as np
import random
import threading
import time
import tkinter as tk
import tkinter.font

from typing import Callable

from hardware.led import Color


class BoxWindow(tk.Frame):
    """
    Tk window with a "button" and "led" acting as a stand-in for the real hardware
    """
    def __init__(self, button_callback: Callable):
        self.master = tk.Tk()
        tk.Frame.__init__(self, self.master)

        self.button_callback = button_callback

        self.status_text = tk.Label(text='off')
        self.status_text.pack()

        self.led = tk.Label(text='⬤', foreground='#000000', font=tkinter.font.Font(size=64))
        self.led.pack()

        self.button = tk.Button(text='', width=4, height=2, background='#AA0000')
        self.button.bind("<ButtonPress>", self._wrap_button_callback)
        # TODO: bind <ButtonRelease> for button hold shutdown condition
        self.button.pack()

        self.master.wm_title("PiBox Sim")
        self.master.geometry("250x200")

    def _wrap_button_callback(self, event: tk.Event):
        self.button_callback()

    def set_led_color(self, color: Color):
        color_string = f'#{color.Red:02x}{color.Green:02x}{color.Blue:02x}'
        self.led['foreground'] = color_string

    def set_callback(self, new_callback: Callable):
        self.button_callback = new_callback


class FakeRGBLED():
    """
    Stand-in for hardware.led.RGBLED to be used with a BoxWindow instance
    """
    def __init__(self, window: BoxWindow, r_pin: int, g_pin: int, b_pin: int):
        logging.info(f'Creating Fake RGB LED referenced to window {window!r}')
        self.window = window
        self.window.status_text['text'] = 'on'

        # Initialize current state
        self._state = "on"
        self._color = Color(0, 0, 0)
        self.update_time = 0.01  # seconds, time that update loop takes

        # Start mainloop
        _t = threading.Thread(target=self._loop)
        _t.start()

    def halt(self):
        self.window.status_text['text'] = 'halt'
        self._state = 'halt'

    def off(self):
        self.set(Color(0, 0, 0))

    def set(self, color: Color):
        self._color = color
        self.window.status_text['text'] = 'on'
        self._state = "on"

    def fade(self, color: Color, period=1):
        self._period = period
        self._color = color
        self.window.status_text['text'] = 'fade'
        self._state = 'fade'

    def blink(self, color: Color, period=1):
        self._period = period
        self._color = color
        self.window.status_text['text'] = 'blink'
        self._state = 'blink'

    def _loop(self):
        while self._state != 'halt':
            if self._state == 'on':
                self.window.set_led_color(self._color)
                time.sleep(self.update_time)

            if self._state == 'fade':
                pause = 0.05
                num_steps = int(self._period / pause / 2)  # number of steps before reversing direction
                up_steps = np.linspace((0, 0, 0), self._color, num_steps)
                steps = np.array(np.concatenate((up_steps, up_steps[::-1])), dtype=int)
                for step in steps:
                    self.window.set_led_color(Color(*step))
                    time.sleep(pause)

            if self._state == 'blink':
                # Turn on
                self.window.set_led_color(self._color)
                time.sleep(self._period / 2.0)
                # Turn off
                self.window.set_led_color(Color(0, 0, 0))
                time.sleep(self._period / 2.0)
