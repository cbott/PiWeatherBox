import sys
from unittest.mock import Mock, patch
sys.modules['RPi'] = Mock()
sys.modules['RPi.GPIO'] = Mock()

from hardware.box import PiBox
from hardware.led import LED

from apps.piweatherbox import WeatherBox

class FakeLED():
    def __init__(self, pin):
        print('Creating Fake LED')

    def halt(self):
        pass

    def off(self):
        self.set(0)

    def set(self, brightness):
        print(f'Set {brightness}')

    def fade(self, period=1):
        print(f'Fade {period}')

    def blink(self, period=1, brightness=100):
        print(f'Blink {period}, {brightness}')


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


def test():
    box = TestBox()
    box._on_press()
    box.mainloop()

def test_weatherbox():
    box = WeatherBox()
    box._on_press()
    box.mainloop()

if __name__ == '__main__':
    test_weatherbox()
