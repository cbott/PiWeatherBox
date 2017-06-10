import RPi.GPIO as gpio
from threading import Thread
import time

RED_PIN = 16
GREEN_PIN = 20
BLUE_PIN = 21
BTN_PIN = 26

REFRESH_TIME = 600 # seconds
LIGHT_TIME = 300 # how long to keep the LED on after pressing the button
SHUTDOWN_TIME = 2 # how long to hold the button to trigger a shutdown

# Weather Constants
TEMP_CHANGE_LARGE = 7 # deg F
TEMP_CHANGE_SMALL = 3 # deg F

from button import TriggerButton
from led import LED
import weather

def update_forecast():
    global temp_change

    wc = weather.conditions()
    while wc is None:
        time.sleep(10)
        wc = weather.conditions()
    print time.strftime("Acquired weather coditions on %B %d at %I:%M:%S")

    hour = time.localtime()[3]
    if hour > 14: # 3 PM or later, give conditions for tomorrow
        prev_temp = wc['today']['high']
        next_temp = wc['tomorrow']['high']
    else: # earlier than 3 PM, give conditions for today
        prev_temp = wc['yesterday']['high']
        next_temp = wc['today']['high']          

    print "Prev Temp:", prev_temp
    print "Next Temp:", next_temp
    temp_change = next_temp - prev_temp

def on_press():
    global led_start_time
    led_start_time = time.time()

try:
    gpio.setmode(gpio.BCM)
    rled = LED(RED_PIN)
    gled = LED(GREEN_PIN)
    bled = LED(BLUE_PIN)
    btn = TriggerButton(BTN_PIN, press_callback = on_press)

    weather_thread = Thread(target = update_forecast)
    weather_thread.daemon = True

    temp_change = 0
    last_update_time = 0
    led_start_time = 0
    shutdown = False
    print "Starting PiWeatherBox Mainloop..."
    while not shutdown:
        # Periodically update forecast asynchronously
        if time.time() - last_update_time > REFRESH_TIME:
            if not weather_thread.is_alive():
                last_update_time = time.time()
                try:
                    weather_thread.start()
                except RuntimeError:
                    weather_thread = Thread(target = self.update_forecast)
                    weather_thread.daemon = True
                    weather_thread.start()

        # Turn on indicator LED for a fixed amount of time after button press
        if time.time() - led_start_time < LIGHT_TIME:
            if temp_change >= TEMP_CHANGE_LARGE:
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
        if btn.get_held() > SHUTDOWN_TIME:
            shutdown = True
            break

        time.sleep(1)
                    

    print "PiWeatherBox shutting down normally..."
    rled.halt()
    gled.halt()
    bled.halt()
    gpio.cleanup()

except (Exception, KeyboardInterrupt) as e:
    print "Exiting due to error condition. Cleaning up first..."
    gpio.cleanup()
    raise
