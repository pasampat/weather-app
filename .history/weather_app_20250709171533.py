import requests
import matplotlib.pyplot as plt
import csv
import os
from datetime import datetime
from tabulate import tabulate




# 🔑 Hardcoded API key
API_KEY = '65f238600d7f98404a0341a139cbc1fc'
BASE_URL = 'https://api.openweathermap.org/data/2.5/weather'

def fetch_weather(city):
    """Fetch 7-day forecast using city name (via lat/lon lookup)."""
    # Step 1: Get lat/lon from city name
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

    # Step 2: Use lat/lon to get 7-day forecast from One Call API
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
    plt.show()


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

    

def parse_weather(data):
    """Extract relevant weather details from API response."""
    temp = data['main']['temp']
    feels_like = data['main']['feels_like']
    description = data['weather'][0]['description']
    city_name = data['name']
    return temp, feels_like, description, city_name

def format_output(city_name, temp, feels_like, description):
    """Display weather information in a clean format."""
    print(f"\nCurrent Weather in {city_name}")
    print(f"Today's Temperature: {temp}°F")
    print(f"Feels Like: {feels_like}°F")
    print(f"Condition: {description.capitalize()}")

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
   


def main():
    # Overwrite the CSV file at the start of the session
    open('forecast_log.csv', 'w').close()
    print("Welcome to the Weather Forecast App!\n")

    while True:
        city_names = []
        temps_list = []
        dates = []  # Reset dates each time to keep them clean

        for i in range(3):
            city = input(f"Enter city #{i+1} (or press Enter to stop early): ").strip()
            if not city:
                break

            try:
                data, city_name = fetch_weather(city)
                forecast_list = data['list']

                # Print current weather info
                current_data = forecast_list[0]
                current_temp = round(current_data['main']['temp'])
                current_description = current_data['weather'][0]['description']
                print(f"\nCurrent Weather in {city_name}")
                print(f"Temperature: {current_temp}°F")
                print(f"Condition: {current_description.capitalize()}")

                # Extract forecast data
                temps = []
                forecast_data = []

                for j in range(0, len(forecast_list), 8):
                    day = forecast_list[j]
                    temp = round(day['main']['temp'])
                    feels_like = round(day['main']['feels_like'])
                    condition = day['weather'][0]['description']
                    readable_date = datetime.fromtimestamp(day['dt']).strftime("%b %d")

                    temps.append(temp)
                    forecast_data.append({
                        "date": readable_date,
                        "temp": temp,
                        "feels_like": feels_like,
                        "condition": condition
                    })

                    if len(dates) < 5:
                        dates.append(readable_date)

                city_names.append(city_name)
                temps_list.append(temps)

                print_city_table(city_name, forecast_data)

            except requests.exceptions.HTTPError as e:
                code = e.response.status_code
                if code == 404:
                    print("City not found. Please try again.")
                elif code == 401:
                    print("Invalid API key. Please check your credentials.")
                    return
                elif code == 429:
                    print("API rate limit exceeded. Try again later.")
                    return
                else:
                    print(f"⚠️ HTTP Error {code}: {e}")
            except requests.exceptions.RequestException as e:
                print(f"Network error. Check your connection.\nDetails: {e}")
            except KeyError as e:
                print(f"Unexpected data format. Missing key: {e}")

        if city_names:
            plot_multi_city_forecast(city_names, temps_list, dates)
            save_forecasts_to_csv('forecast_log.csv', city_names, temps_list)

            # Identify hottest and coldest
            hottest = {"temp": float('-inf')}
            coldest = {"temp": float('inf')}
            for city, temps in zip(city_names, temps_list):
                for i, temp in enumerate(temps):
                    if temp > hottest["temp"]:
                        hottest = {"temp": temp, "city": city, "day": dates[i]}
                    if temp < coldest["temp"]:
                        coldest = {"temp": temp, "city": city, "day": dates[i]}

            print(f"\nHottest Day: {hottest['day']} in {hottest['city']} ({hottest['temp']}°F)")
            print(f"Coldest Day: {coldest['day']} in {coldest['city']} ({coldest['temp']}°F)")

        while True:
            again = input("\nEnter 3 new cities and compare again? (y/n): ").strip().lower()
            if again == 'y':
                break
            elif again == 'n':
                print("\nGoodbye! Your forecasts are saved in forecast_log.csv.")
                return
            else:
                print("Please enter only 'y' or 'n'.")



if __name__ == "__main__":
    main()

