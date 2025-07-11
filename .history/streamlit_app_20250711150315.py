import streamlit as st
from weather_utils import get_weather_data, format_forecast_data, plot_forecast_chart, find_extreme_days
# Import any other functions you’ve written that you’ll reuse

st.set_page_config(page_title="Weather App", page_icon="🌤️")
st.title("🌤️ Weather Forecast")
st.write("Enter up to 3 city names to see their 5-day weather forecast.")

# Input Section
city_input = st.text_input("Cities (comma-separated):")

if st.button("Get Forecast"):
    cities = [city.strip() for city in city_input.split(",") if city.strip()]
    
    if not cities:
        st.warning("Please enter at least one city.")
    else:
        st.write(f"Fetching data for: {', '.join(cities)}")
        # We’ll wire up the forecast logic next
