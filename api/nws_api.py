# For interacting with National Weather Service public weather API
# Incomplete, for future reference only
# https://www.weather.gov/documentation/services-web-api#/default/gridpoint_forecast_hourly
import logging
from datetime import datetime
from typing import List

import requests

HEADERS = {"User-Agent": "piweatherbox"}

LAT = 1
LON = 1

POINTS_API = "https://api.weather.gov/points/{lat},{lon}"

active_forecast = None
yesterday_forecast = None


def parse_date(datestring: str) -> datetime:
    # Remove -07:00 from "%Y-%m-%dT%H:%M:%S-07:00"
    datestring = datestring.rsplit("-", 1)[0]
    return datetime.strptime(datestring, "%Y-%m-%dT%H:%M:%S-07:00")


def conditions():
    try:
        adr = POINTS_API.format(lat=LAT, lon=LON)
        resp = requests.get(adr, headers=HEADERS)

        if resp.status_code != 200:
            logging.error(f'Invalid response status <{resp.status_code}> getting weather {adr}')
            return None

        forecast_adr = resp.json()["properties"]["forecast"]
        resp = requests.get(forecast_adr, headers=HEADERS)

        if resp.status_code != 200:
            logging.error(f'Invalid response status <{resp.status_code}> getting weather {forecast_adr}')
            return None

        forecast_response = resp.json()
        periods: List = forecast_response["properties"]["periods"]

        if periods[0]["name"] == "Tonight":
            yesterday = None
            today = None
            tomorrow = periods[1]
        else:
            yesterday = None
            today = periods[0]
            tomorrow = periods[2]

        if active_forecast is None or parse_date(forecast["endTime"]) > parse_date(active_forecast["endTime"]):
            yesterday_forecast = active_forecast
            active_forecast = forecast

        tomorrow_rain = tomorrow["probabilityOfPrecipitation"]["value"]  # % chance
        tomorrow_high = tomorrow["temperature"]

    except ValueError as e:  # json.decoder.JSONDecodeError in python 3.5+
        logging.error(f'Error parsing API response: {e}')
    except Exception as e:
        logging.error(f'An unexpected error occurred while receiving weather data: {e}')
    return None
