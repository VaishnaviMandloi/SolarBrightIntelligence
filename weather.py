import requests
# from datetime import datetime, timedelta

url = 'https://api.open-meteo.com/v1/forecast'


def getWeatherData(latitude, longitude, start_date):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ["weather_code", "precipitation", "soil_temperature_6cm", "vapour_pressure_deficit"],
        "daily": "sunshine_duration",
        "daily": ["sunrise", "sunset", "sunshine_duration"],
        "temperature_unit": "fahrenheit",
        "timezone": "GMT",
        "start_date": start_date,
        "end_date": start_date
    }
    try:
        responses = requests.get(url, params=params)
        if responses.status_code == 200:
            return responses.json()
        else:
            return 'weather api error'
    except:
        return 'weather api error'


# print(getWeatherData(52.52, 13.419998, '2024-03-13'))
