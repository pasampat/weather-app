from weather_utils import (
    fetch_weather,
    plot_forecast,
    plot_multi_city_forecast,
    save_forecasts_to_csv,
    get_weather_note,
    print_city_table,
)
from datetime import datetime
import requests

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
                print(f"\nCurrent Weather in {city_name}: {current_temp}°F, {current_description.capitalize()}")
                # Extract forecast data
                temps = []
                forecast_data = []
                #40 forecast - one every 3 hours - 8 per day over 5 days
                #
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
