import tkinter as tk
import tkinter.font

from collections import namedtuple
from typing import Callable

# Duplicated from hardware.LED to avoid needing to import
Color = namedtuple('Color', ['Red', 'Green', 'Blue'])


def duty_cycle_to_intensity(duty_cycle: float) -> int:
    """
    Converts a 0-100 duty cycle to a 0-255 color intensity
    Inverse of intensity_to_duty_cycle() from hardware.led
    """
    return int(duty_cycle * 255.0 / 100.0)


class BoxWindow(tk.Frame):
    """
    Tk window with a "button" and "led" acting as a stand-in for the real hardware
    """
    # Map "hardware" pin numbers to colors
    RED_PIN = 16
    GREEN_PIN = 20
    BLUE_PIN = 21

    def __init__(self, button_callback: Callable):
        # Store current RGB color values of the Fake LED (0-255)
        self.current_color = {
            self.RED_PIN: 0,
            self.GREEN_PIN: 0,
            self.BLUE_PIN: 0
        }

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
        self._update_color()

    def _wrap_button_callback(self, event: tk.Event):
        self.button_callback()

    def set_led_channel_duty_cycle(self, pin: int, duty_cycle: float):
        self.current_color[pin] = duty_cycle_to_intensity(duty_cycle)

    def _update_color(self):
        """
        Refresh the display every 50ms
        If we try to call this every time the color updates it slows things down way too much
        """
        r = self.current_color[self.RED_PIN]
        g = self.current_color[self.GREEN_PIN]
        b = self.current_color[self.BLUE_PIN]
        color_string = f'#{r:02x}{g:02x}{b:02x}'
        self.led['foreground'] = color_string

        self.master.after(50, self._update_color)

    def set_callback(self, new_callback: Callable):
        self.button_callback = new_callback


class FakePWM:
    """ Stand-in for RPi.GPIO.pwm to pass the relevant commands to the BoxWindow sim """
    def __init__(self, window: BoxWindow, pin: int, freq: int):
        self.pin = pin
        self.window = window

    def start(self, dutycycle: float):
        self.window.set_led_channel_duty_cycle(self.pin, dutycycle)

    def ChangeDutyCycle(self, dutycycle: float):
        self.window.set_led_channel_duty_cycle(self.pin, dutycycle)

    def stop(self):
        pass
