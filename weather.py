import json
import time
import urllib
from urllib.request import urlopen

API_KEY = ""
with open("apikey.txt", "r") as f:
    API_KEY = f.readline().strip()


def conditions():
    """ Return relevant weather conditions for yesterday, today, and tomorrow

    Return value is a dictionary containing
    { yesterday_high, today_high, today_rain, today_text, tomorrow_high, tomorrow_rain }
    or None if an error occurs
    """
    url_yesterday = 'http://api.wunderground.com/api/%s/geolookup/yesterday/q/MI/Ann_Arbor.json' % API_KEY
    url_forecast = 'http://api.wunderground.com/api/%s/geolookup/forecast/q/MI/Ann_Arbor.json' % API_KEY

    try:
        yesterday = json.loads(urlopen(url_yesterday).read().decode('utf8'))
        forecast = json.loads(urlopen(url_forecast).read().decode('utf8'))

        yesterday_high = float(yesterday['history']['dailysummary'][0]['maxtempi'])

        today_high = float(forecast['forecast']['simpleforecast']['forecastday'][0]['high']['fahrenheit'])
        today_rain = float(forecast['forecast']['simpleforecast']['forecastday'][0]['qpf_allday']['in'])
        today_text = forecast['forecast']['txt_forecast']['forecastday'][0]['fcttext']

        tomorrow_high = float(forecast['forecast']['simpleforecast']['forecastday'][1]['high']['fahrenheit'])
        tomorrow_rain = float(forecast['forecast']['simpleforecast']['forecastday'][1]['qpf_allday']['in'])

        return {'yesterday': {'high': yesterday_high},
                'today': {'high': today_high, 'rain': today_rain, 'conditions': today_text},
                'tomorrow': {'high': tomorrow_high, 'rain': tomorrow_rain}}
    except urllib.error.URLError as e:
        print(time.strftime("Error contacting Wunderground API on %B %d at %H:%M:%S --"), e)
    except ValueError as e:  # json.decoder.JSONDecodeError in python 3.5+
        print(time.strftime("Error parsing Wunderground response on %B %d at %H:%M:%S --"), e)
    except Exception as e:
        print(time.strftime("An unexpected error occurred while receiving weather data on %B %d at %H:%M:%S --"), e)
    return None


if __name__ == "__main__":
    # Example usage
    from time import sleep

    print("Grabbing data...")
    while True:
        c = conditions()
        if c:
            break
        sleep(8)

    print("Yesterday's High Temperature:", c['yesterday']['high'])
    print("Today's High Temperature:", c['today']['high'])
    print("Today:", c['today']['conditions'])
    print("Rain Today:", c['today']['rain'])
    print("Tomorrow's High Temperature", c['tomorrow']['high'])
    print("Rain Tomorrow:", c['tomorrow']['rain'])
