import logging

import requests

WEATHER_URL = 'http://api.openweathermap.org/data/2.5/weather'


class Weather():
    """
    Represents a location's weather data.
    """

    def __init__(self, temperature, humidity, pressure, description):
        self.temperature = temperature
        self.humidity = humidity
        self.pressure = pressure
        self.description = description


def get_weather(latitude, longitude):
    params = {'lat': latitude, 'lon': longitude, 'units': 'metric'}
    result = requests.get(WEATHER_URL, params=params)
    try:
        data = result.json()
    except:
        logging.error('Weather API call failed: {}'.format(result.status_code))
        return None

    # Create the Weather object from the json data.
    temp = data['main']['temp']
    humidity = data['main']['humidity']
    pressure = data['main']['pressure']
    desc = data['weather'][0]['main'] + ': ' + data['weather'][0]['description']
    return Weather(temp, humidity, pressure, desc)
