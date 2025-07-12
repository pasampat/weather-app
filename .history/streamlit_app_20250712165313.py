import streamlit as st
import requests
from weather_utils import (
    fetch_weather,
    plot_forecast,
    plot_multi_city_forecast,
    save_forecasts_to_csv,
    get_weather_note,
    print_city_table,
    parse_5day_forecast,
    get_city_forecast
)
# Import any other functions you’ve written that you’ll reuse

st.set_page_config(page_title="Weather App", page_icon="🌤️")
st.title("🌤️ Weather Forecast")
st.markdown("Enter up to 3 city names to see their 5-day weather forecast.")

if "csv_initialized" not in st.session_state:
    # First load -> wipe the file
    open("forecast_log.csv", "w").close()
    st.session_state.csv_initialized = True


# Input Section
city_input = st.text_input("Cities (comma-separated):").strip()

# Show buttons side by side
col1, col2 = st.columns([1, 1])
with col1:
    get_clicked = st.button("Get Forecast")
with col2:
    clear_clicked = st.button("Clear Cities")

# Handle "Clear" click first
if clear_clicked:
    st.rerun()

# Handle "Get Forecast" click
if get_clicked:
    all_cities_entered = [c.strip() for c in city_input.split(",") if c.strip()]

    # Optional info if more than 3 entered
    if len(all_cities_entered) > 3:
        st.info("Only the first 3 cities will be used.")

    cities = all_cities_entered[:3]

    if len(cities) == 1 and " " in cities[0]:
        st.warning("Did you forget commas? Try: `london, paris, tokyo`")
        st.stop()

    if not cities:
        st.warning("Please enter at least one city.")
        st.stop()

    # --- Forecast logic (everything else you had) ---
    city_names = []
    temps_list = []
    date_labels = None

    for city in cities:
        try:
            display_name, five_day = get_city_forecast(city)

            st.subheader(f"📍 {display_name}")

            table_data = []
            temps_this_city = []

            for day in five_day:
                note = get_weather_note(day["condition"].lower())
                table_data.append(
                    [day["date"],
                     f'{day["temp"]}°F',
                     day["condition"].capitalize(),
                     f'{day["feels_like"]}°F',
                     note]
                )
                temps_this_city.append(day["temp"])

            st.table(
                {"Date": [row[0] for row in table_data],
                 "Temp": [row[1] for row in table_data],
                 "Condition": [row[2] for row in table_data],
                 "Feels Like": [row[3] for row in table_data],
                 "Note": [row[4] for row in table_data]}
            )

            city_names.append(display_name)
            temps_list.append(temps_this_city)
            if date_labels is None:
                date_labels = [d["date"] for d in five_day]


        except requests.exceptions.HTTPError as e:
            code = e.response.status_code
            if code == 404:
                st.error(f"❌ `{city}` not found. Please check spelling.")
            elif code == 401:
                st.error("❌ Invalid API key.")
            elif code == 429:
                st.error("⏳ API rate limit exceeded. Try again later.")
            else:
                st.error(f"HTTP Error {code}: {e}")
        except requests.exceptions.RequestException as e:
            st.error(f"🌐 Network error while fetching `{city}`: {e}")
        except KeyError as e:
            st.error(f"⚠️ Unexpected data format for `{city}`. Missing key: {e}")
        except Exception as e:
            st.error(f"Unexpected error while processing `{city}`: {e}")
        

    if city_names:
        st.subheader("📈 Temperature Trend (All Cities)")
        fig = plot_multi_city_forecast(city_names, temps_list, date_labels)
        st.pyplot(fig)

        save_forecasts_to_csv("forecast_log.csv", city_names, temps_list)
        # Let user download the file
        st.success("Forecasts saved to forecast_log.csv")
        
        # Safely calculate hottest/coldest only if at least 1 city succeeded
        hottest = {"temp": float('-inf')}
        coldest = {"temp": float('inf')}

        for city, temps in zip(city_names, temps_list):
            for i, temp in enumerate(temps):
                if temp > hottest["temp"]:
                    hottest = {"temp": temp, "city": city, "day": date_labels[i]}
                if temp < coldest["temp"]:
                    coldest = {"temp": temp, "city": city, "day": date_labels[i]}

        st.markdown(f"🔥 **Hottest Day**: {hottest['day']} in {hottest['city']} ({hottest['temp']}°F)")
        st.markdown(f"❄️ **Coldest Day**: {coldest['day']} in {coldest['city']} ({coldest['temp']}°F)")
