# TODO: Sort these imports please
import RPi.GPIO as gpio
from abc import ABC, abstractmethod
import time
from typing import Any, Callable
import logging
from hardware.button import TriggerButton
from hardware.led import LED
import threading
import sys

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                    datefmt='%B %d, %Y %H:%M:%S')

class PiBox(ABC):
    """ Base class to handle hardware and control flow for any PiBox application """
    # Raspberry Pi GPIO Pins:
    RED_PIN = 16
    GREEN_PIN = 20
    BLUE_PIN = 21
    BTN_PIN = 26

    def __init__(self):
        # Initialize hardware
        gpio.setmode(gpio.BCM)
        self.rled = LED(PiBox.RED_PIN)
        self.gled = LED(PiBox.GREEN_PIN)
        self.bled = LED(PiBox.BLUE_PIN)
        self.btn = TriggerButton(PiBox.BTN_PIN, press_callback=self._on_press)

        # Initialize internal state
        self.last_press_time = 0
        self.last_update_time = 0
        self.api_call_result = None

        # Initialize settings
        # Override in subclass to acheive desired behavior
        self.refresh_time_s = 60 * 60  # Time between calls to the API
        self.led_on_time_s = 60 * 5  # Time for LED to remain on after button press
        self.loop_delay_s = 0.1  # Seconds to sleep between each run of the main loop
        self.shutdown_time_s = 2  # Seconds to hold the button to trigger a shutdown
        self.obsolescence_time_s = 10800  # Seconds to keep old data if unable to update

    @abstractmethod
    def api_call(self) -> Any:
        """
        Override this method to implement application-specific behavior
        Returns a value that will be passed to `led_control()` as the `data` parameter
        """
        ...

    @abstractmethod
    def led_control(self, data: Any):
        """
        Override this method to implement application-specific behavior
        Make use of self.rled,gled,bled
        """
        ...

    def _nonblocking_api_call(self):
        """ Runs the actual API call repeatedly without blocking the main thread
            TODO: Rename
        """
        self._running = True
        while self._running:
            if time.time() - self.last_update_time > self.refresh_time_s:
                try:
                    logging.info('Calling API')
                    # TODO: Should we have some way of terminating if call takes too long?
                    self.api_call_result = self.api_call()
                    self.last_update_time = time.time()
                    logging.info(f'API call returned {self.api_call_result}')
                except Exception as e:
                    logging.error(f'Received exception {e} while running API call. Restarting.')

    def mainloop(self):
        try:
            logging.info('Starting PiBox Mainloop')
            api_thread = threading.Thread(target=self._nonblocking_api_call)
            api_thread.start()

            while True:
                # Turn on indicator LED for a fixed amount of time after button press
                if time.time() - self.last_press_time < self.led_on_time_s:
                    if time.time() - self.last_update_time > self.obsolescence_time_s:
                        # Failure to update conditions: Solid purple
                        # TODO: Maybe make this a method call to allow custom behavior for subclasses?
                        self.rled.set(100)
                        self.gled.off()
                        self.bled.set(50)
                    else:
                        self.led_control(self.api_call_result)
                else:
                    self.rled.off()
                    self.gled.off()
                    self.bled.off()

                # Shutdown when button is held
                if self.btn.is_pressed() and (self.btn.get_held() > self.shutdown_time_s):
                    return

                sys.stdout.flush()
                time.sleep(self.loop_delay_s)

        except (Exception, KeyboardInterrupt):
            self._cleanup()
            raise

    def _on_press(self):
        """ Callback function for button press """
        logging.debug('Button pressed')
        self.last_press_time = time.time()

    def _cleanup(self):
        self._running = False  # End the API call thread
        self.rled.halt()
        self.gled.halt()
        self.bled.halt()
        gpio.cleanup()
        logging.debug('Ran Cleanup')

    def __del__(self):
        self._cleanup()