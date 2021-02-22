import tkinter as tk
import tkinter.font
import random
import threading
import time

from hardware.led import Color

class BoxWindow(tk.Frame):
    """
    Tk window with a "button" and "led" acting as a stand-in for the real hardware
    """
    def __init__(self, button_callback):
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

    def halt(self):
        self.box_reference.status_text['text'] = 'off'

    def off(self):
        self.set(Color(0, 0, 0))

    def set(self, color: Color):
        self.box_reference.status_text['text'] = 'on'
        self.box_reference.set_led_color(color)

    def fade(self, color: Color, period=1):
        self.box_reference.status_text['text'] = 'fade'
        self.box_reference.set_led_color(color)

    def blink(self, color: Color, period=1):
        self.box_reference.status_text['text'] = 'blink'
        self.box_reference.set_led_color(color)
