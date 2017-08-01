import RPi.GPIO as gpio
import sys
import threading
import time

RED_PIN = 16
GREEN_PIN = 20
BLUE_PIN = 21
BTN_PIN = 26

REFRESH_TIME = 1800 # seconds, time between weather updates
LIGHT_TIME = 300 # how long to keep the LED on after pressing the button
SHUTDOWN_TIME = 2 # how long to hold the button to trigger a shutdown

# Weather Constants
TEMP_CHANGE_LARGE = 7 # deg F
TEMP_CHANGE_SMALL = 3 # deg F
RAIN_THRESHOLD = 0.1 # inches

from button import TriggerButton
from led import LED
import weather

def update_forecast():
    global temp_change
    global upcoming_rain

    wc = weather.conditions()
    if not threading.main_thread().is_alive():
            return
    while wc is None:
        for i in range(10):
            time.sleep(1)
            if not threading.main_thread().is_alive():
                return
        wc = weather.conditions()
    print(time.strftime("Acquired weather coditions on %B %d at %H:%M:%S"))

    hour = time.localtime()[3]
    if hour > 14: # 3 PM or later, give conditions for tomorrow
        prev_temp = wc['today']['high']
        next_temp = wc['tomorrow']['high']
        next_rain = wc['tomorrow']['rain']
    else: # earlier than 3 PM, give conditions for today
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

try:
    gpio.setmode(gpio.BCM)
    rled = LED(RED_PIN)
    gled = LED(GREEN_PIN)
    bled = LED(BLUE_PIN)
    btn = TriggerButton(BTN_PIN, press_callback = on_press)

    weather_thread = threading.Thread(target = update_forecast)

    temp_change = 0
    upcoming_rain = 0
    last_update_time = 0
    led_start_time = 0
    rain_light_time = 0

    shutdown = False
    print("Starting PiWeatherBox Mainloop...")
    while not shutdown:
        # Periodically update forecast asynchronously
        if time.time() - last_update_time > REFRESH_TIME:
            if not weather_thread.is_alive():
                last_update_time = time.time()
                try:
                    weather_thread.start()
                except RuntimeError:
                    weather_thread = threading.Thread(target = update_forecast)
                    weather_thread.start()

        # Turn on indicator LED for a fixed amount of time after button press
        if time.time() - led_start_time < LIGHT_TIME:
            if upcoming_rain >= RAIN_THRESHOLD and time.time() - rain_light_time > 3:
                # Every 3 seconds, blink yellow if it's going to rain
                rain_light_time = time.time()
                rled.set(100)
                gled.set(50)
                bled.off()
                # otherwise just set the LED to indicate temperature
            elif temp_change >= TEMP_CHANGE_LARGE:
                rled.fade()
                gled.off()
                bled.off()
            elif temp_change >= TEMP_CHANGE_SMALL:
                rled.set(100)
                gled.off()
                bled.off()
            elif temp_change > -TEMP_CHANGE_SMALL:
                rled.off()
                gled.set(100)
                bled.off()
            elif temp_change > -TEMP_CHANGE_LARGE:
                rled.off()
                gled.off()
                bled.set(100)
            else:
                rled.off()
                gled.off()
                bled.fade()
        else:
            rled.off()
            gled.off()
            bled.off()

        # Shutdown when button is held
        if btn.get_pressed() and (btn.get_held() > SHUTDOWN_TIME):
            shutdown = True
            break

        sys.stdout.flush()
        time.sleep(1)
                    

    print("PiWeatherBox shutting down normally...")
    cleanup()

except (Exception, KeyboardInterrupt) as e:
    print("Exiting due to error condition. Cleaning up first...")
    cleanup()
    raise
