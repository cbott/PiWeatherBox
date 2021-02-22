import random
import sys
import threading
import time

from unittest.mock import Mock, patch
sys.modules['RPi'] = Mock()
sys.modules['RPi.GPIO'] = Mock()

from apps.piweatherbox import WeatherBox
from hardware.box import PiBox
from hardware.led import Color
from tests.box_sim import *


class TestBox(PiBox):
    """ Does some random stuff to test functionality """
    def __init__(self):
        super().__init__()
        self.refresh_time_s = 20
        self.led_on_time_s = 10

    def api_call(self):
        return random.randint(1,10)

    def led_control(self, data):
        if data < 5:
            self.led.fade(Color(0, 255, 0))
        else:
            self.led.set(Color(0, 128, 255))


def test_thread():

    fake_box = BoxWindow(button_callback=lambda : True)

    def gen(*args):
        return FakeRGBLED(fake_box, *args)

    with patch('hardware.box.RGBLED', gen):
        # Create real box
        box = TestBox()
        fake_box.set_callback(box._on_press)

        # Run real box in thread
        logic_thread = threading.Thread(target=box.mainloop)
        logic_thread.start()

        # Run fake box as main process, piping commands to real box
        fake_box.mainloop()

        # Kill real box thread
        box._running = False

if __name__ == '__main__':
    test_thread()
