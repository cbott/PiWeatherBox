import RPi.GPIO as gpio
import sys
import threading
import time

from button import TriggerButton
from led import LED
import weather

try:
    from authenticate import attempt_authentication
except ImportError:
    def attempt_authentication():
        pass

# Raspberry Pi GPIO Pins:
RED_PIN = 16
GREEN_PIN = 20
BLUE_PIN = 21
BTN_PIN = 26

# Weatherbox configuration constants:
REFRESH_TIME = 1800        # Seconds between weather updates
OBSOLESCENCE_TIME = 10800  # Seconds to keep old weather data if unable to update
LIGHT_TIME = 300           # Seconds to keep the LED on after pressing the button
SHUTDOWN_TIME = 2          # Seconds to hold the button to trigger a shutdown
LOOP_DELAY = 0.1           # Seconds to sleep between each run of the main loop
RAIN_LIGHT_FREQ = 3        # Seconds to wait between flashes of the rain indicator
RAIN_LIGHT_DURRATION = 1   # Seconds to keep rain indicator on each flash

# Prior to mid-day, weatherbox will indicate the forecast conditions for today
# After mid-day, weatherbox will indicate forecast conditions for tomorrow
MID_DAY = 14  # Hours (24 hr clock)

# LED color-change thresholds:
LARGE_TEMP_CHANGE = 7  # deg F
SMALL_TEMP_CHANGE = 3  # deg F
RAIN_THRESHOLD = 0.1   # inches (QPF)


def update_forecast():
    global temp_change
    global upcoming_rain

    last_contact = time.time()

    wc = weather.conditions()
    if not threading.main_thread().is_alive():
            return
    while wc is None:
        attempt_authentication()  # If network fails, attempt to authenticate before retrying
        for i in range(15):
            # Wait for 15 seconds before next attempt, but shut down if main program has ended
            time.sleep(1)
            if not threading.main_thread().is_alive():
                return
        wc = weather.conditions()

        if time.time() - last_contact > OBSOLESCENCE_TIME:
            # If network connection is lost for extended amount of time, indicate by setting parameters to None
            temp_change = None
            upcoming_rain = None

    print(time.strftime("Acquired weather coditions on %B %d at %H:%M:%S"))

    hour = time.localtime()[3]
    if hour > MID_DAY:
        # Give conditions for tomorrow
        prev_temp = wc['today']['high']
        next_temp = wc['tomorrow']['high']
        next_rain = wc['tomorrow']['rain']
    else:
        # Give conditions for today
        prev_temp = wc['yesterday']['high']
        next_temp = wc['today']['high']
        next_rain = wc['today']['rain']

    print("Prev Temp:", prev_temp)
    print("Next Temp:", next_temp)
    print("Next Rain:", next_rain)
    temp_change = next_temp - prev_temp
    upcoming_rain = next_rain


def on_press():
    global led_start_time
    led_start_time = time.time()


def cleanup():
    rled.halt()
    gled.halt()
    bled.halt()
    gpio.cleanup()


def mainloop():
    global led_start_time
    global temp_change
    global upcoming_rain

    weather_thread = threading.Thread(target=update_forecast)

    temp_change = None
    upcoming_rain = None
    last_update_time = 0
    led_start_time = 0
    rain_light_time = 0

    while True:
        # Periodically update forecast asynchronously
        if time.time() - last_update_time > REFRESH_TIME:
            if not weather_thread.is_alive():
                last_update_time = time.time()
                try:
                    weather_thread.start()
                except RuntimeError:
                    weather_thread = threading.Thread(target=update_forecast)
                    weather_thread.start()

        # Turn on indicator LED for a fixed amount of time after button press
        if time.time() - led_start_time < LIGHT_TIME:
            # Read in global variables a single time to avoid threading issues
            threadsafe_upcoming_rain = upcoming_rain
            threadsafe_temp_change = temp_change

            if threadsafe_upcoming_rain is None or threadsafe_temp_change is None:
                # Failure to update conditions: Solid purple
                rled.set(100)
                gled.off()
                bled.set(50)
            elif threadsafe_upcoming_rain >= RAIN_THRESHOLD and (time.time() - rain_light_time) < RAIN_LIGHT_DURRATION:
                # Every 3 seconds, blink yellow if it's going to rain
                rled.set(100)
                gled.set(50)
                bled.off()
                # otherwise just set the LED to indicate temperature
            elif threadsafe_temp_change >= LARGE_TEMP_CHANGE:
                # Much warmer: Fade red
                rled.fade()
                gled.off()
                bled.off()
            elif threadsafe_temp_change >= SMALL_TEMP_CHANGE:
                # Warmer: Solid red
                rled.set(100)
                gled.off()
                bled.off()
            elif threadsafe_temp_change > -SMALL_TEMP_CHANGE:
                # About the same: Solid green
                rled.off()
                gled.set(100)
                bled.off()
            elif threadsafe_temp_change > -LARGE_TEMP_CHANGE:
                # Colder: Solid blue
                rled.off()
                gled.off()
                bled.set(100)
            else:
                # Much colder: Fade blue
                rled.off()
                gled.off()
                bled.fade()

            if time.time() - rain_light_time > RAIN_LIGHT_FREQ:
                # Reset timer tracking when to light up rain indicator
                rain_light_time = time.time()

        else:
            rled.off()
            gled.off()
            bled.off()

        # Shutdown when button is held
        if btn.is_pressed() and (btn.get_held() > SHUTDOWN_TIME):
            return

        sys.stdout.flush()
        time.sleep(LOOP_DELAY)


if __name__ == "__main__":
    try:
        gpio.setmode(gpio.BCM)
        rled = LED(RED_PIN)
        gled = LED(GREEN_PIN)
        bled = LED(BLUE_PIN)
        btn = TriggerButton(BTN_PIN, press_callback=on_press)

        print("Starting PiWeatherBox Mainloop...")

        mainloop()

        print("PiWeatherBox shutting down normally...")

    except (Exception, KeyboardInterrupt):
        print("Exiting due to error condition. Cleaning up first...")
        raise

    finally:
        cleanup()
