from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime, timedelta
from decouple import config

import requests
import json
from .models import WeatherData

# Create your views here.

API_KEY = config('API_KEY')

geo_code = 'http://api.openweathermap.org/geo/1.0/direct?q={}&limit={}&appid={}'
current_weather = 'https://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}'
forecast = 'https://api.openweathermap.org/data/2.5/forecast/daily?lat={}&lon={}&cnt={}&appid={}'

def index(request):
   
    if request.method == "POST":
        city = request.POST['city']

        # try:

        weather_data,daily_forecast = fetch_weather_and_forecast(city)

        context = {
            "weather_data" : weather_data,
            "daily_forecast" : daily_forecast
        }
        return render(request,'appweather/index.html',context)
        # except Exception as e:
        #     print(e)
            # return HttpResponse("An error occured while fetching the data, Please try after sometimes..")
    else:
        return render(request,'appweather/index.html')
    


def fetch_weather_and_forecast(city):

    try:
        geo_response = requests.get(geo_code.format(city,1,API_KEY)).json()
        print(geo_response,"*********************************************")

        if len(geo_response) == 0:
            raise Exception("City not found or invalid API response")

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
            "description": current_weather_response['weather'][0]['description'],
            "icon" : current_weather_response['weather'][0]['icon']
        }

        WeatherData.objects.create(
            city= city,
            temperature= round(current_weather_response['main']['temp'] - 273.15, 2),
            humidity = current_weather_response['main']['humidity'],
            description=current_weather_response['weather'][0]['description'],
            icon=current_weather_response['weather'][0]['icon'],
            
        )

        daily_forecast = []
        for daily_data in forecast_response['daily'][:5]:
            daily_forecast.append({
                'day' : datetime.fromtimestamp(daily_data['dt']).strftime("%A"),
                'min_temp' : round(daily_data['temp']['min'] - 273.15,2),
                'max_temp' : round(daily_data['temp']['max'] - 273.15,2),
                'humidity' : daily_data['humidity'],
                'description' : daily_data['weather'][0]['description'],
                'icon' : daily_data['weather'][0]['icon']
            }) 
        return weather_data,daily_forecast
    except Exception as e:
        print(e)
        raise


def calculate_average_temperature():
    now = datetime.now()
    one_day_ago = now - timedelta(days=1)

    temperatures = WeatherData.objects.filter(created_at__range=[one_day_ago, now])

    if temperatures.exists():
        avg_temp = sum([t.temperature for t in temperatures]) / len(temperatures)
    else:
        avg_temp = 0  # Or another default value

    return avg_temp



def check_extreme_conditions(request):
    avg_temp = calculate_average_temperature()
    if avg_temp > 30:  # Example threshold
        return HttpResponse("High temperature alert!")
    else:
        return HttpResponse("Normal temperature.")