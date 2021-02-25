# test_local.py
# Runs PiBox simulation to test without RPi hardware access

import sys
import threading
import time

from unittest.mock import Mock, patch
sys.modules['RPi'] = Mock()
sys.modules['RPi.GPIO'] = Mock()

from apps.testapp import TestBox
from tests.box_sim import *


def run_local_test():
    """ Runs Box hardware class in thread, along with box simulator GUI """
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
    run_local_test()
