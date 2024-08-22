from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime, timedelta
from decouple import config
from django.utils import timezone

import requests
import json
from .models import WeatherData

# Create your views here.

API_KEY = config('API_KEY')

geo_code = 'http://api.openweathermap.org/geo/1.0/direct?q={}&limit={}&appid={}'
current_weather = 'https://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}'
forecast = 'https://api.openweathermap.org/data/2.5/forecast/daily?lat={}&lon={}&cnt={}&appid={}'

from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    weather_data = None
    avg_temp = None
    error_message = None

    if request.method == "POST":
        city = request.POST.get('city', '').strip()

        if not city:
            error_message = "Please enter a city name."
        else:
            try:
                weather_data = fetch_weather_and_forecast(city)
                if weather_data is None or 'error' in weather_data:
                    error_message = "City not found or weather data is unavailable. Please try again."
                else:
                    avg_temp = calculate_average_temperature()
            except Exception as e:
                error_message = "An error occurred while fetching the data. Please try again later."

    # Reset weather_data after POST or if it's a GET request
    if request.method == "GET":
        weather_data = None

    context = {
        "weather_data": weather_data,
        "avg_temp": avg_temp,
        "error_message": error_message
    }
    return render(request, 'appweather/index.html', context)


    


def fetch_weather_and_forecast(city):

    try:
        geo_response = requests.get(geo_code.format(city,1,API_KEY)).json()
        print(geo_response,"*******************GEO RESPONSE**************************")

        if not geo_response:
            return None

        lat = geo_response[0]['lat']
        lon = geo_response[0]['lon']

        print(lat,lon,"*****************11111111111111111111111111111111111*****************")

        current_weather_response = requests.get(current_weather.format(lat,lon,API_KEY)).json()

        lat,lon =current_weather_response['coord']['lat'],current_weather_response['coord']['lon']

        print(lat,lon,"*****************22222222222222222222222222222222222222222*****************")

        forecast_response = requests.get(forecast.format(lat,lon,7, API_KEY)).json()

        print(forecast_response,"****************************************************************")

        weather_data = {
            'city': city,
            'temperature': round(current_weather_response['main']['temp'] - 273.15,2),
            'humidity' : current_weather_response['main']['humidity'],
            'wind' : round(current_weather_response['wind']['speed'] * 3.6,2),
            "description": current_weather_response['weather'][0]['description'],
            "icon" : current_weather_response['weather'][0]['icon']
        }

        WeatherData.objects.create(
            city= city,
            temperature= round(current_weather_response['main']['temp'] - 273.15, 2),
            humidity = current_weather_response['main']['humidity'],
            wind = round(current_weather_response['wind']['speed'] * 3.6,2),
            description=current_weather_response['weather'][0]['description'],
            icon=current_weather_response['weather'][0]['icon'],
            timestamp=timezone.now()
            
        )

        # daily_forecast = []
        # for daily_data in forecast_response['daily'][:5]:
        #     daily_forecast.append({
        #         'day' : datetime.fromtimestamp(daily_data['dt']).strftime("%A"),
        #         'min_temp' : round(daily_data['temp']['min'] - 273.15,2),
        #         'max_temp' : round(daily_data['temp']['max'] - 273.15,2),
        #         'humidity' : daily_data['humidity'],
        #         'description' : daily_data['weather'][0]['description'],
        #         'icon' : daily_data['weather'][0]['icon']
        #     }) 
        return weather_data
    except Exception as e:
        print(e)
        raise


def calculate_average_temperature():
    now = timezone.now()
    one_day_ago = now - timedelta(days=1)

    temperatures = WeatherData.objects.filter(timestamp__range=[one_day_ago, now])

    if temperatures.exists():
        avg_temp = round(sum([t.temperature for t in temperatures]) / len(temperatures),2)
    else:
        avg_temp = 0  # Or another default value

    return avg_temp



def check_extreme_conditions():
    avg_temp = calculate_average_temperature()
    if avg_temp > 30:
        return HttpResponse("High temperature alert!")
    elif avg_temp < 15:
        return HttpResponse("Low temperature alert.")
    else:
        return HttpResponse("Temperature is within a normal range.")

