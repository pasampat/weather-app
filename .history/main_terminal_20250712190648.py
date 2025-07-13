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
    """
    Main loop for the Weather Forecast App.

    - Clears the forecast_log.csv at the start, so each session starts fresh
    - Prompts user for up to 3 cities per run (can stop early).
    - For each city:
        - Fetches forecast data using fetch_weather (calls the API).
        - Prints current weather for that city.
        - Extracts one forecast per day from the API's 3-hour-interval data.
        - Builds lists for plotting, CSV, and pretty table
    - After all cities are entered:
        - Plots the forecasts together for comparison.
        - Saves all city forecasts to CSV file.
        - Finds and displays the overall hottest and coldest day/city.
    - Offers the user the chance to run again with new cities or exit
    - Handles network errors, API key errors, and user typos gracefully
    """
    open('forecast_log.csv', 'w').close()  # clear (overwrite) CSV file at the start
    print("Welcome to the Weather Forecast App!\n")
    while True:
        city_names = []      # Stores formatted city names (from API) for this round
        temps_list = []      # Each city's list of daily temps (for plotting & csv)
        dates = []           # Holds up to 5 date strings (only need to build this once per round)
        for i in range(3):   # User can enter up to 3 cities
            city = input(f"Enter city #{i+1} (or press Enter to stop early): ").strip()
            if not city:
                break  # Allow user to do less than 3 cities
            try:
                # fetch_weather gets all forecast data + standardized city name
                data, city_name = fetch_weather(city)
                forecast_list = data['list']  # List of 3-hour chunks (40 total for 5 days)

                # Show the current weather using the first chunk in the forecast
                current_data = forecast_list[0]
                current_temp = round(current_data['main']['temp'])
                current_description = current_data['weather'][0]['description']
                print(f"\nCurrent Weather in {city_name}: {current_temp}°F, {current_description.capitalize()}")

                temps = []         # Holds just 5 temps (one per day)
                forecast_data = [] # Each day's forecast (for table)

                # OWM API gives 40 forecasts (3hr intervals) - we want one per day (every 8th)
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
                    # Only add dates for first 5 unique days, one time per round
                    if len(dates) < 5:
                        dates.append(readable_date)
                city_names.append(city_name)
                temps_list.append(temps)
                print_city_table(city_name, forecast_data)  # Pretty-print the table for this city

            except requests.exceptions.HTTPError as e:
                code = e.response.status_code
                # Handle common API errors in a user-friendly way
                if code == 404:
                    print("City not found. Please try again.")
                elif code == 401:
                    print("Invalid API key. Please check your credentials.")
                    return  # Can't continue, so exit
                elif code == 429:
                    print("API rate limit exceeded. Try again later.")
                    return
                else:
                    print(f"⚠️ HTTP Error {code}: {e}")
            except requests.exceptions.RequestException as e:
                print(f"Network error. Check your connection.\nDetails: {e}")
            except KeyError as e:
                print(f"Unexpected data format. Missing key: {e}")

        # After all cities have been entered (if at least one), process results
        if city_names:
            # Plot forecasts for all entered cities on one chart (using real dates)
            plot_multi_city_forecast(city_names, temps_list, dates)
            # Save all city forecasts for this round to the CSV file
            save_forecasts_to_csv('forecast_log.csv', city_names, temps_list)

            # Find the hottest and coldest day across all cities (linear search)
            hottest = {"temp": float('-inf')}
            coldest = {"temp": float('inf')}
            for city, temps in zip(city_names, temps_list):
                for i, temp in enumerate(temps):
                    # i is the day index (0–4), use for date lookup
                    if temp > hottest["temp"]:
                        hottest = {"temp": temp, "city": city, "day": dates[i]}
                    if temp < coldest["temp"]:
                        coldest = {"temp": temp, "city": city, "day": dates[i]}
            print(f"\nHottest Day: {hottest['day']} in {hottest['city']} ({hottest['temp']}°F)")
            print(f"Coldest Day: {coldest['day']} in {coldest['city']} ({coldest['temp']}°F)")

        # User menu: run again or quit
        while True:
            again = input("\nEnter 3 new cities and compare again? (y/n): ").strip().lower()
            if again == 'y':
                break   # Start a new round
            elif again == 'n':
                print("\nGoodbye! Your forecasts are saved in forecast_log.csv.")
                return
            else:
                print("Please enter only 'y' or 'n'.")

    
if __name__ == "__main__":
    main()
