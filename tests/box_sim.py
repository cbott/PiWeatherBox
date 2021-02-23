import numpy as np
import random
import threading
import tkinter as tk
import tkinter.font
import time

from hardware.led import Color

class BoxWindow(tk.Frame):
    """
    Tk window with a "button" and "led" acting as a stand-in for the real hardware
    """
    def __init__(self, button_callback):
        # TODO: black window background
        self.master = tk.Tk()
        tk.Frame.__init__(self, self.master)

        self.button_callback = button_callback

        self.status_text = tk.Label(text='off')
        self.status_text.pack()

        self.led = tk.Label(text='⬤', foreground='#000000', font=tkinter.font.Font(size=64))
        self.led.pack()

        self.button = tk.Button(text='', width=4, height=2, background='#AA0000', command=self._wrap_button_callback)
        self.button.pack()

        self.master.wm_title("PiBox Sim")
        self.master.geometry("250x200")

    def _wrap_button_callback(self):
        self.button_callback()

    def set_led_color(self, color: Color):
        color_string = f'#{color.Red:02x}{color.Green:02x}{color.Blue:02x}'
        self.led['foreground'] = color_string

    def set_random_color(self):
        self.set_led_color(Color(random.randint(0,255), random.randint(0,255), random.randint(0,255)))

    def set_callback(self, new_callback):
        self.button_callback = new_callback


class FakeRGBLED():
    def __init__(self, box_reference: BoxWindow, r_pin: int, g_pin: int, b_pin: int):
        print(f'Creating Fake RGB LED referenced to window {box_reference}')
        self.box_reference = box_reference  # TODO: rename
        self.box_reference.status_text['text'] = 'on'

        # Initialize current state
        self._state = "on"
        self._color = Color(0, 0, 0)
        self.update_time = 0.01  # seconds, time that update loop takes

        # Start mainloop
        _t = threading.Thread(target=self._loop)
        _t.start()

    def halt(self):
        self.box_reference.status_text['text'] = 'halt'
        self._state = 'halt'

    def off(self):
        self.set(Color(0, 0, 0))

    def set(self, color: Color):
        self._color = color
        self.box_reference.status_text['text'] = 'on'
        self._state = "on"

    def fade(self, color: Color, period=1):
        self._period = period
        self._color = color
        self.box_reference.status_text['text'] = 'fade'
        self._state = 'fade'

    def blink(self, color: Color, period=1):
        self._period = period
        self._color = color
        self.box_reference.status_text['text'] = 'blink'
        self._state = 'blink'

    def _loop(self):
        while self._state != 'halt':
            if self._state == 'on':
                self.box_reference.set_led_color(self._color)
                time.sleep(self.update_time)

            if self._state == 'fade':
                pause = 0.05
                num_steps = int(self._period / pause / 2)  # number of steps before reversing direction
                up_steps = np.linspace((0, 0, 0), self._color, num_steps)
                steps = np.array(np.concatenate((up_steps, up_steps[::-1])), dtype=int)
                for step in steps:
                    self.box_reference.set_led_color(Color(*step))
                    time.sleep(pause)

            if self._state == 'blink':
                # Turn on
                self.box_reference.set_led_color(self._color)
                time.sleep(self._period / 2.0)
                # Turn off
                self.box_reference.set_led_color(Color(0, 0, 0))
                time.sleep(self._period / 2.0)
