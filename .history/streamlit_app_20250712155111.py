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
city_input = st.text_input("Cities (comma-separated):").strip()
    all_cities_entered = [c.strip() for c in city_input.split(",") if c.strip()]
    if len(all_cities_entered) > 3:
        st.info("Only the first 3 cities will be used.")

    cities = all_cities_entered[:3]


if st.button("Get Forecast"):
    cities = [c.strip() for c in city_input.split(",") if c.strip()][:3]
        # Detect common formatting mistake (no commas)
    if len(cities) == 1 and " " in cities[0]:
        st.warning("Did you forget commas? Try: `london, paris, tokyo`")
        st.stop()

    if not cities:
        st.warning("Please enter at least one city.")
        st.stop()

    # containers to accumulate multi-city data for the chart
    city_names = []
    temps_list  = []
    date_labels = None          # we’ll set this once

    for city in cities:
        try:
            display_name, five_day = get_city_forecast(city)

            # ----- UI output per city -----
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

            # ----- collect for combined chart -----
            city_names.append(display_name)
            temps_list.append(temps_this_city)
            if date_labels is None:
                date_labels = [d["date"] for d in five_day]

        except Exception as e:
            st.error(f"⚠️ {city}: {e}")

    # ----- show combined chart if ≥1 city succeeded -----
    if city_names:
        st.subheader("📈 Temperature Trend (All Cities)")
        fig = plot_multi_city_forecast(city_names, temps_list, date_labels)
        st.pyplot(fig)
