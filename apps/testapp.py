# testapp.py
# Example PiBox app implementation

import random

from hardware.box import PiBox
from hardware.led import Color

class TestBox(PiBox):
    """ Bare minimum PiBox implementation to show functionality """
    def __init__(self):
        super().__init__()
        self.refresh_time_s = 20
        self.led_on_time_s = 10

    def api_call(self):
        return random.randint(1,3)

    def led_control(self, data):
        if data == 1:
            self.led.fade(Color(0, 255, 0))
        elif data == 2:
            self.led.blink(Color(0, 128, 255))
        else:
            self.led.set(Color(128, 128, 255))
