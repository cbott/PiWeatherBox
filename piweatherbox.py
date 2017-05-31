import RPi.GPIO as gpio
import time

BTN_PIN = 5
RED_PIN = 6
GREEN_PIN = 13
BLUE_PIN = 19

REFRESH_TIME = 10 # minutes

from led import LED
import weather

try:
    gpio.setmode(gpio.BCM)
    rled = LED(RED_PIN)
    gled = LED(GREEN_PIN)
    bled = LED(BLUE_PIN)

    while 1:
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
        dt = next_temp - prev_temp
        rled.off()
        gled.off()
        bled.off()

        if dt >= 8:
            rled.fade()
        elif dt >= 3:
            rled.set(100)
        elif dt > -3:
            gled.set(50)
        elif dt > -8:
            bled.set(100)
        else:
            bled.fade()

        time.sleep(REFRESH_TIME * 60)


    gpio.cleanup()

except (Exception, KeyboardInterrupt) as e:
    print "Cleaning Up"
    gpio.cleanup()
    raise
