import logging
import requests
import time
import os

CONFIG_FILE = 'weather_config.txt'

# Load config file
config_path = os.path.join(os.path.dirname(__file__), CONFIG_FILE)
with open(config_path, 'r') as f:
    contents = f.readlines()
    if len(contents) != 3:
        raise ValueError('Config file requires 3 lines: api key, latitude, longitude')
    API_KEY = contents[0].strip()
    LAT = contents[1].strip()
    LON = contents[2].strip()

ONE_DAY = 60 * 60 * 24  # Seconds in a day


def conditions():
    """ Return relevant weather conditions for yesterday, today, and tomorrow

    Return value is a dictionary containing
    { yesterday_high, today_high, today_rain, today_text, tomorrow_high, tomorrow_rain }
    or None if an error occurs
    """
    exc = 'currently,minutely,hourly,alerts'

    url_yesterday = 'https://api.darksky.net/forecast/{apikey}/{latitude},{longitude},{time}?exclude={exclude}'
    url_forecast = 'https://api.darksky.net/forecast/{apikey}/{latitude},{longitude}?exclude={exclude}'

    try:
        yesterday_time = int(time.time() - ONE_DAY)  # UNIX timestamp of some point during yesterday

        urls = {'yesterday': url_yesterday.format(apikey=API_KEY, latitude=LAT, longitude=LON, time=yesterday_time, exclude=exc),
                'forecast': url_forecast.format(apikey=API_KEY, latitude=LAT, longitude=LON, exclude=exc)}
        responses = []
        for url in urls:
            resp = requests.get(urls[url])
            if resp.status_code != 200:
                logging.error(f'Invalid response status <{resp.status_code}> getting weather {url}')
                return None
            responses.append(resp.json())
        yesterday = responses[0]
        forecast = responses[1]

        yesterday_high = float(yesterday['daily']['data'][0]['temperatureHigh'])

        today_high = float(forecast['daily']['data'][0]['temperatureHigh'])
        today_rain = float(forecast['daily']['data'][0].get('precipIntensityMax', -1))  # inches of liquid water per hour
        today_text = forecast['daily']['data'][0].get('summary', '')

        tomorrow_high = float(forecast['daily']['data'][1]['temperatureHigh'])
        tomorrow_rain = float(forecast['daily']['data'][1].get('precipIntensityMax', -1))

        return {'yesterday': {'high': yesterday_high},
                'today': {'high': today_high, 'rain': today_rain, 'conditions': today_text},
                'tomorrow': {'high': tomorrow_high, 'rain': tomorrow_rain}}
    except ValueError as e:  # json.decoder.JSONDecodeError in python 3.5+
        logging.error(f'Error parsing API response: {e}')
    except Exception as e:
        logging.error(f'An unexpected error occurred while receiving weather data: {e}')
    return None


if __name__ == '__main__':
    # Example usage
    from time import sleep

    print('Grabbing data...')
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
