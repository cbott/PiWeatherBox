import logging
import sys
import threading
import time

from abc import ABC, abstractmethod
from typing import Any, Callable

import RPi.GPIO as gpio

from hardware.button import TriggerButton
from hardware.led import *


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
        self.led = RGBLED(PiBox.RED_PIN, PiBox.GREEN_PIN, PiBox.BLUE_PIN)
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
        self.api_retry_delay_s = 15  # Seconds to wait before calling API again after failure

    @abstractmethod
    def api_call(self) -> Any:
        """
        Called repeatedly with a period of refresh_time_s
        Override this method to implement application-specific behavior

        Returns a value that will be passed to `led_control()` as the `data` parameter
        Raises any exception to indicate failure, after which method will be called again after self.api_retry_delay_s
        """
        ...

    @abstractmethod
    def led_control(self, data: Any):
        """
        Called repeatedly with a period of loop_delay_s whenever the LED should be active
        Override this method to implement application-specific behavior

        Variables:
            data - Value returned by `api_call()`
            self.led - RGBLED object to command
        """
        ...

    def led_stale(self):
        """
        Indicate stale data/inability to update
        Optionally override in subclass for application-specific behavior
        """
        self.led.set(Color(255, 0, 128))

    def _api_call_wrapper(self):
        """ Runs the actual API call repeatedly without blocking the main thread """
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
                    # Delay next call for api_retry_delay_s
                    self.last_update_time = time.time() - self.refresh_time_s + self.api_retry_delay_s

    def mainloop(self):
        self._running = True  # Allows for killing mainloop if running in thread

        try:
            logging.info('Starting PiBox Mainloop')
            api_thread = threading.Thread(target=self._api_call_wrapper)
            api_thread.start()

            while self._running:
                # Turn on indicator LED for a fixed amount of time after button press
                if time.time() - self.last_press_time < self.led_on_time_s:
                    if time.time() - self.last_update_time > self.obsolescence_time_s:
                        # Failure to update conditions: Solid purple
                        self.led_stale()
                    else:
                        self.led_control(self.api_call_result)
                else:
                    self.led.off()

                # Shutdown when button is held
                if self.btn.is_pressed() and (self.btn.get_held() > self.shutdown_time_s):
                    return

                sys.stdout.flush()
                time.sleep(self.loop_delay_s)

            logging.info('PiBox mainloop exited')

        finally:
            self._cleanup()

    def _on_press(self):
        """ Callback function for button press """
        logging.debug('Button pressed')
        self.last_press_time = time.time()

    def _cleanup(self):
        self._running = False  # End the API call thread
        self.led.halt()
        gpio.cleanup()
        logging.debug('Ran Cleanup')

    def __del__(self):
        self._cleanup()
