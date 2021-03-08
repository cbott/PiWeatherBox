# test_hardware.py
# Runs the PiBox test app on RPi hardware

import logging

from apps.testapp import TestBox


def run_hardware_test():
    """ Runs TestBox """
    box = TestBox()
    print("Starting TestBox Mainloop...")
    box.mainloop()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s',
                        datefmt='%B %d, %Y %H:%M:%S')
    run_hardware_test()
