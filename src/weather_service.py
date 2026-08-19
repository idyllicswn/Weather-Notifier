import requests
import logging

logger = logging.getLogger(__name__)

def fetch_weather_report(latitude,longitude,location):
    #base URLS for open-Mateo weather and air quality APIs
    weather_url = "https://api.open-meteo.com/v1/forecast"
    aqi_url = "https://air-quality-api.open-meteo.com/v1/air-quality"

    #weather request parameters
    weather_params = {
        "latitude": latitude,
        "longitude": longitude,
        "current_weather": True,
        "daily": "temperature_2m_max,temperature_2m_min", # requests 7 day max/min temp
        "timezone": "auto" #autu detects timezone based on GPS
    }

    #air quality request parameters
    aqi_params={
        "latitude": latitude,
        "longitude": longitude,
        "current":"us_aqi,pm2_5"#fetches US AQI score and fine particulate matter
    }

    try:
        #FETCHING WEATHER
        w_response = requests.get(weather_url,params=weather_params)
        w_response.raise_for_status()
        w_data = w_response.json()

        #extracting current weather values
        current = w_data["current_weather"]
        temp=current["temperature"]
        wind=current["windspeed"]

        # daily forecast list
        daily = w_data["daily"]
        dates=daily["time"]
        max_temps = daily["temperature_2m_max"]
        min_temps = daily["temperature_2m_min"]

        #FETCHING AIR QUALITY
        a_response=requests.get(aqi_url,params=aqi_params)
        a_response.raise_for_status()
        a_data=a_response.json()

        #extract AQI and PM2.5 readings
        us_aqi = a_data["current"]["us_aqi"]
        pm2_5 = a_data["current"]["pm2_5"]

        #DETERMINING HEALTH CATEGORY ACC TO STANDARD SCALE
        if us_aqi<=50:
            aqi_status ="GOOD"
        elif us_aqi<=100:
            aqi_status = "MODERATE"
        elif us_aqi<=150:
            aqi_status= "UNHEALTHY FOR SENSITIVE GROUPS"
        elif us_aqi<=200:
            aqi_status = "UNHEALTHY"
        else:
            aqi_status = "DANGEROUS"

        #SUMMARY
        summary=(
        f"---Weather Report of {location}\n"
        f" Temp: {temp}°C |  Wind: {wind} km/h\n"
        f"AQI: {us_aqi} ({aqi_status}) | PM2.5: {pm2_5} µg/m³\n\n"
        f"3-Day Forecast:\n"
        f"-> {dates[0]}: Max {max_temps[0]}°C / Min {min_temps[0]}°C\n"
        f"-> {dates[1]}: Max {max_temps[1]}°C / Min {min_temps[1]}°C\n"
        f"-> {dates[2]}: Max {max_temps[2]}°C / Min {min_temps[2]}°C"
        )
        logger.info("Successfully formatted weather report.")
        return summary

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch weather/AQI data: {e}")
        return None


