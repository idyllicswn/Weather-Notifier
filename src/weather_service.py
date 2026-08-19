import requests
import logging

logger = logging.getLogger(__name__)

# Map Open-Meteo WMO weather codes to human-readable condition text
WEATHER_CODES = {
    0: "Clear / Sunny",
    1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
    45: "Foggy", 48: "Depositing Rime Fog",
    51: "Light Drizzle", 53: "Moderate Drizzle", 55: "Dense Drizzle",
    61: "Slight Rain", 63: "Moderate Rain", 65: "Heavy Rain",
    71: "Slight Snow", 73: "Moderate Snow", 75: "Heavy Snow",
    80: "Slight Rain Showers", 81: "Moderate Rain Showers", 82: "Violent Rain Showers",
    95: "Thunderstorm", 96: "Thunderstorm with Hail"
}

def fetch_weather_report(latitude, longitude, location):
    weather_url = "https://api.open-meteo.com/v1/forecast"
    aqi_url = "https://air-quality-api.open-meteo.com/v1/air-quality"

    weather_params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,wind_speed_10m,weather_code", # Added weather_code
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto"
    }

    aqi_params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "us_aqi,pm2_5"
    }

    try:
        w_response = requests.get(weather_url, params=weather_params)
        w_response.raise_for_status()
        w_data = w_response.json()

        current = w_data["current"]
        temp = current["temperature_2m"]
        wind = current["wind_speed_10m"]
        code = current["weather_code"]
        
        # Look up condition string
        condition = WEATHER_CODES.get(code, "Unknown")

        daily = w_data["daily"]
        dates = daily["time"]
        max_temps = daily["temperature_2m_max"]
        min_temps = daily["temperature_2m_min"]

        a_response = requests.get(aqi_url, params=aqi_params)
        a_response.raise_for_status()
        a_data = a_response.json()

        us_aqi = a_data["current"]["us_aqi"]
        pm2_5 = a_data["current"]["pm2_5"]

        if us_aqi <= 50:
            aqi_status = "GOOD"
        elif us_aqi <= 100:
            aqi_status = "MODERATE"
        elif us_aqi <= 150:
            aqi_status = "UNHEALTHY FOR SENSITIVE GROUPS"
        elif us_aqi <= 200:
            aqi_status = "UNHEALTHY"
        else:
            aqi_status = "DANGEROUS"

        summary = (
            f"---Weather Report of {location}\n"
            f" Condition: {condition}\n"
            f" Temp: {temp}°C | Wind: {wind} km/h\n"
            f"AQI: {us_aqi} ({aqi_status}) | PM2.5: {pm2_5} µg/m³\n\n"
            f"3-Day Forecast:\n"
            f"-> {dates[0]}: Max {max_temps[0]}°C / Min {min_temps[0]}°C\n"
            f"-> {dates[1]}: Max {max_temps[1]}°C / Min {min_temps[1]}°C\n"
            f"-> {dates[2]}: Max {max_temps[2]}°C / Min {min_temps[2]}°C"
        )
        
        logger.info("Successfully formatted weather report.")
        return summary, temp, us_aqi, aqi_status

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch weather/AQI data: {e}")
        return None, None, None, None