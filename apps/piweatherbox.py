import logging
import time
from api import weather
from hardware.box import PiBox
from hardware.led import Color

# Prior to mid-day, weatherbox will indicate the forecast conditions for today
# After mid-day, weatherbox will indicate forecast conditions for tomorrow
MID_DAY = 14  # Hours (24 hr clock)

# LED color-change thresholds:
LARGE_TEMP_CHANGE = 7  # deg F
SMALL_TEMP_CHANGE = 3  # deg F
RAIN_THRESHOLD = 0.04  # inches (QPF)
RAIN_LIGHT_FREQ = 3        # Seconds to wait between flashes of the rain indicator
RAIN_LIGHT_DURRATION = 1   # Seconds to keep rain indicator on each flash


class WeatherBox(PiBox):
    def __init__(self):
        super().__init__()
        self.rain_light_time = 0

    def api_call(self):
        logging.debug('Retrieving conditions')
        wc = weather.conditions()

        if not wc:
            raise ValueError('Failed to retrieve conditions')

        logging.debug('Acquired weather conditions')

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

        logging.info(f'Prev Temp: {prev_temp}')
        logging.info(f'Next Temp: {next_temp}')
        logging.info(f'Next Rain: {next_rain}')
        temp_change = next_temp - prev_temp
        upcoming_rain = next_rain

        return {'temp_change': temp_change, 'upcoming_rain': upcoming_rain}

    def led_control(self, data):
        upcoming_rain = data['upcoming_rain']
        temp_change = data['temp_change']
        if upcoming_rain >= RAIN_THRESHOLD and (time.time() - self.rain_light_time) < RAIN_LIGHT_DURRATION:
            # Every 3 seconds, blink yellow if it's going to rain
            self.led.set(Color(255, 128, 0))
            # otherwise just set the LED to indicate temperature
        elif temp_change >= LARGE_TEMP_CHANGE:
            # Much warmer: Fade red
            self.led.fade(Color(255, 0, 0))
        elif temp_change >= SMALL_TEMP_CHANGE:
            # Warmer: Solid red
            self.led.set(Color(255, 0, 0))
        elif temp_change > -SMALL_TEMP_CHANGE:
            # About the same: Solid green
            self.led.set(Color(0, 255, 0))
        elif temp_change > -LARGE_TEMP_CHANGE:
            # Colder: Solid blue
            self.led.set(Color(0, 0, 255))
        else:
            # Much colder: Fade blue
            self.led.fade(Color(0, 0, 255))

        if time.time() - self.rain_light_time > RAIN_LIGHT_FREQ:
            # Reset timer tracking when to light up rain indicator
            self.rain_light_time = time.time()


if __name__ == "__main__":
    print("Starting PiWeatherBox Mainloop...")
    weatherbox = WeatherBox()
    weatherbox.mainloop()
