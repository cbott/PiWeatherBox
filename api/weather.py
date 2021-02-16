import requests
import time

API_KEY = ""
with open("api/apikey.txt", "r") as f:
    API_KEY = f.readline().strip()


ONE_DAY = 60 * 60 * 24  # Seconds in a day

def conditions():
    """ Return relevant weather conditions for yesterday, today, and tomorrow

    Return value is a dictionary containing
    { yesterday_high, today_high, today_rain, today_text, tomorrow_high, tomorrow_rain }
    or None if an error occurs
    """
    lat = 42.262151
    lon = -83.706412
    exc = "currently,minutely,hourly,alerts"

    url_yesterday = "https://api.darksky.net/forecast/{apikey}/{latitude},{longitude},{time}?exclude={exclude}"
    url_forecast = "https://api.darksky.net/forecast/{apikey}/{latitude},{longitude}?exclude={exclude}"

    try:
        yesterday_time = int(time.time() - ONE_DAY)  # UNIX timestamp of some point during yesterday
        yesterday_resp = requests.get(url_yesterday.format(apikey=API_KEY, latitude=lat, longitude=lon, time=yesterday_time, exclude=exc))
        if yesterday_resp.status_code != 200:
            print(time.strftime("Invalid response status <{}> getting info for yesterday on %B %d at %H:%M:%S --".format(yesterday_resp.status_code)))
            return None
        yesterday = yesterday_resp.json()

        forecast_resp = requests.get(url_forecast.format(apikey=API_KEY, latitude=lat, longitude=lon, exclude=exc))
        if forecast_resp.status_code != 200:
            print(time.strftime("Invalid response status <{}> getting forecast on %B %d at %H:%M:%S --".format(forecast_resp.status_code)))
            return None
        forecast = forecast_resp.json()

        yesterday_high = float(yesterday["daily"]["data"][0]["temperatureHigh"])

        today_high = float(forecast["daily"]["data"][0]["temperatureHigh"])
        today_rain = float(forecast["daily"]["data"][0].get("precipIntensityMax", -1))  # inches of liquid water per hour
        today_text = forecast["daily"]["data"][0].get("summary", "")

        tomorrow_high = float(forecast["daily"]["data"][1]["temperatureHigh"])
        tomorrow_rain = float(forecast["daily"]["data"][1].get("precipIntensityMax", -1))

        return {'yesterday': {'high': yesterday_high},
                'today': {'high': today_high, 'rain': today_rain, 'conditions': today_text},
                'tomorrow': {'high': tomorrow_high, 'rain': tomorrow_rain}}
    except ValueError as e:  # json.decoder.JSONDecodeError in python 3.5+
        print(time.strftime("Error parsing API response on %B %d at %H:%M:%S --"), e)
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
