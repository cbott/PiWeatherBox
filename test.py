import sys
from unittest.mock import Mock, patch
sys.modules['RPi'] = Mock()
sys.modules['RPi.GPIO'] = Mock()

from apps.piweatherbox import WeatherBox
from hardware.box import PiBox
from tests.box_sim import *
import threading


class TestBox(PiBox):
    def __init__(self):
        super().__init__()
        self.refresh_time_s = 20

    def api_call(self):
        return 1

    def led_control(self, data):
        print(f'LED Control: {data}')
        if data:
            self.rled.set(100)
            self.gled.set(0)
            self.bled.set(0)
        else:
            self.rled.set(0)
            self.gled.set(100)
            self.bled.set(0)


@patch('hardware.box.LED', FakeLED)
def test_basic():
    box = TestBox()
    box._on_press()
    box.mainloop()

def test_weatherbox():
    box = WeatherBox()
    box._on_press()
    box.mainloop()

def test_thread():
    # Create real box

    fake_box = BoxWindow(button_callback=lambda : True)

    def gen(*args):
        return FakeRGBLED(fake_box, *args)

    with patch('hardware.box.RGBLED', gen):
        box = WeatherBox()
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
