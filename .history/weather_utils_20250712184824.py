from dotenv import load_dotenv
import os
load_dotenv()

import requests
import matplotlib.pyplot as plt
import csv
import os
from datetime import datetime
from tabulate import tabulate

API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise ValueError("API_KEY not found. Please define it in your .env file.")



def fetch_weather(city):
    # lat/lon from city name
    geo_url = 'https://api.openweathermap.org/data/2.5/weather'
    geo_params = {
        'q': city,
        'appid': API_KEY,
        'units': 'imperial'
    }
    geo_response = requests.get(geo_url, params=geo_params)
    geo_response.raise_for_status()
    geo_data = geo_response.json()
    lat = geo_data['coord']['lat']
    lon = geo_data['coord']['lon']

    # u lat/lon to get forecast from One Call API
    one_call_url = 'https://api.openweathermap.org/data/2.5/forecast'
    one_call_params = {
        'lat': lat,
        'lon': lon,
        'exclude': 'minutely,hourly,alerts',
        'appid': API_KEY,
        'units': 'imperial'
    }
    weather_response = requests.get(one_call_url, params=one_call_params)
    weather_response.raise_for_status()
    return weather_response.json(), geo_data['name']  


def plot_forecast(city_name, temps):
    """Plot 5-day temperature forecast for a single city."""
    days = [f"Day {i+1}" for i in range(len(temps))]

    plt.plot(days, temps, marker='o', label=city_name)
    plt.title("5-Day Temperature Forecast")
    plt.xlabel("Day")
    plt.ylabel("Temperature (°F)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_multi_city_forecast(city_names, temps_list, dates):
    """Plot 5-day temperature forecasts for multiple cities using real dates."""
    for city_name, temps in zip(city_names, temps_list):
        plt.plot(dates, temps, marker='o', label=city_name)

    plt.title("5-Day Temperature Forecast (Multiple Cities)")
    plt.xlabel("Date")
    plt.ylabel("Temperature (°F)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    #plt.show()
    return plt.gcf()


def save_forecasts_to_csv(filename, city_names, temps_list):
    """Save city forecasts to a CSV file."""
    needs_header = not os.path.isfile(filename) or os.path.getsize(filename) == 0

    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)

        if needs_header:
            header = ['City'] + [f'Day {i+1}' for i in range(len(temps_list[0]))]
            writer.writerow(header)

        for city, temps in zip(city_names, temps_list):
            row = [city] + temps
            writer.writerow(row)

    print(f"\nForecasts saved to {filename}")



def get_weather_note(condition):
    """Return emoji tip based on condition."""
    if "rain" in condition:
        return "☔ Bring a jacket"
    elif "clear" in condition:
        return "🧴 Wear sunscreen"
    elif "snow" in condition:
        return "❄️ Dress warm"
    elif "cloud" in condition:
        return "☁️ Cloudy day"
    else:
        return ""

def print_city_table(city_name, forecast_data):
    """
    Display a 5-day forecast table for a city.
    Each forecast entry is a dictionary with 'date', 'temp', 'condition', 'feels_like'
    """
    print(f"\n5-Day Forecast for {city_name}:\n")

    table = []
    for i, entry in enumerate(forecast_data, 1):
        temp = f"{entry['temp']}°F"
        feels = f"{entry['feels_like']}°F"
        note = get_weather_note(entry['condition'].lower())
        table.append([i, entry['date'], temp, entry['condition'].capitalize(), feels, note])

    headers = ["Day", "Date", "Temp", "Condition", "Feels Like", "Note"]
    print(tabulate(table, headers=headers, tablefmt="grid"))
   

def parse_5day_forecast(forecast_json):
    """
    Return a list of 5 dicts — one per day — each with
    date, temp, feels_like, and condition.
    """
    forecast_list = forecast_json["list"]
    parsed = []
    for i in range(0, len(forecast_list), 8):  # 3-h steps → one per day
        slot = forecast_list[i]
        parsed.append(
            {
                "date": datetime.fromtimestamp(slot["dt"]).strftime("%b %d"),
                "temp": round(slot["main"]["temp"]),
                "feels_like": round(slot["main"]["feels_like"]),
                "condition": slot["weather"][0]["description"],
            }
        )
    return parsed[:5]  # safety

def get_city_forecast(city: str):
    """
    High-level helper:  ➜ raw JSON, city_display_name, parsed_5day_list
    Raises the same requests exceptions you already handle.
    """
    raw_json, display_name = fetch_weather(city)
    parsed_5day = parse_5day_forecast(raw_json)
    return display_name, parsed_5day


