import RPi.GPIO as gpio
import time


class TriggerButton:
    """ A button that triggers events when pressed or held for a length of time """
    def __init__(self, pin, press_callback=lambda: None):
        self.pin = pin
        self.press_callback = press_callback

        gpio.setup(self.pin, gpio.IN)
        gpio.add_event_detect(self.pin, gpio.BOTH, callback=self._on_event, bouncetime=50)

        self._presstime = time.time()
        self._active = False

    def get_pressed(self):
        # Returns whether or not the button is currently pressed
        return gpio.input(self.pin)

    def get_held(self):
        # Returns how long the button has been pressed for
        # Or how long it has been unpressed for (indicated as a negative value)
        if self._active:
            return time.time() - self._presstime
        else:
            return self._presstime - time.time()

    def _on_event(self, channel):
        if self.get_pressed():
            self._active = True
            self._presstime = time.time()
            self.press_callback()
        else:
            self._active = False
            self._presstime = time.time()


if __name__ == "__main__":
    BUTTON_PIN = 26
    gpio.setmode(gpio.BCM)

    try:
        btn = TriggerButton(BUTTON_PIN)

        print("Doing Stuff")
        while btn.get_held() < 3:
            time.sleep(0.1)
        print("Shutting Down...")
    except KeyboardInterrupt:
        print("Keyboard Interrupt. Shutting Down...")

    finally:
        gpio.cleanup()
