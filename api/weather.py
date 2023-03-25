import logging
import os

import requests

# Open-Meteo API: https://open-meteo.com/
API_BASE = "https://api.open-meteo.com"
API = "/v1/forecast?latitude={lat}&longitude={lon}"
CONFIG_FILE = 'weather_config.txt'

# Load config file
config_path = os.path.join(os.path.dirname(__file__), CONFIG_FILE)
with open(config_path, 'r') as f:
    contents = f.readlines()
    if len(contents) != 2:
        raise ValueError('Config file requires 2 lines: latitude, longitude')
    LAT = contents[0].strip()
    LON = contents[1].strip()


params = {
    "forecast_days": "2",
    "timezone": "auto",
    "past_days": "1",
    "daily": "temperature_2m_max,precipitation_sum",
    "temperature_unit": "fahrenheit",
    "precipitation_unit": "inch",
}


def conditions():
    """ Return relevant weather conditions for yesterday, today, and tomorrow

    Return value is a dictionary containing
    { yesterday_high, today_high, today_rain, today_text, tomorrow_high, tomorrow_rain }
    or None if an error occurs
    """
    try:
        request_url = API_BASE + API.format(lat=LAT, lon=LON)

        response = requests.get(request_url, params=params)
        if response.status_code != 200:
            logging.error(f'Invalid response status <{response.status_code}> getting weather {response.url}')
            return None
        data = response.json()

        temperature_max = data["daily"]["temperature_2m_max"]
        precipitation = data["daily"]["precipitation_sum"]
        result = {
            'yesterday': {'high': temperature_max[0]},
            'today': {'high': temperature_max[1], 'rain': precipitation[1], 'conditions': ""},
            'tomorrow': {'high': temperature_max[2], 'rain': precipitation[2]}
        }

        return result
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
