import streamlit as st
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

# Input Section
