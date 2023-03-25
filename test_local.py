# test_local.py
# Runs PiBox simulation to test without RPi hardware access
import logging
import sys
import threading
from unittest.mock import Mock, patch

# Mock the Pi-Specific imports that would otherwise fail with module not found. Methods will be mocked later
sys.modules['RPi'] = Mock()
sys.modules['RPi.GPIO'] = Mock()

# Mock any API modules - application specific behavior will be specified below
sys.modules['api'] = Mock()

from tests.box_sim import *

# Application Specific
########################################
API_MODULE = 'api.weather'


class FakeAPI:
    """ Update FakeAPI methods to correctly mock the behavior of the real API in api/ """
    def __init__(self):
        pass

    def conditions(self):
        return {'yesterday': {'high': 65}, 'today': {'high': 66, 'rain': 1, 'conditions': 'weather'}, 'tomorrow': {'high': 90, 'rain': 0}}
#########################################


def run_local_test():
    """ Runs Box hardware class in thread, along with box simulator GUI """
    fake_box = BoxWindow(button_callback=lambda: True)

    def fake_pwm_factory(pin, freq):
        return FakePWM(fake_box, pin, freq)

    fakeapi = FakeAPI()

    with patch('RPi.GPIO.PWM', fake_pwm_factory), patch(API_MODULE, fakeapi):
        ########################################
        from apps.piweatherbox import WeatherBox
        box = WeatherBox()
        ########################################

        fake_box.set_callback(box._on_press)

        # Run real box in thread
        logic_thread = threading.Thread(target=box.mainloop)
        logic_thread.start()

        # Run fake box as main process, piping commands to real box
        fake_box.mainloop()

        # Kill real box thread
        box._running = False


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s',
                        datefmt='%B %d, %Y %H:%M:%S')
    run_local_test()
