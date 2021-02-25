# test_hardware.py
# Runs the PiBox test app on RPi hardware

from apps.testapp import TestBox


def run_hardware_test():
    """ Runs TestBox """
    box = TestBox()
    print("Starting TestBox Mainloop...")
    box.mainloop()


if __name__ == '__main__':
    run_hardware_test()
