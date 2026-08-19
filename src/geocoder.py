import requests
import logging

logger = logging.getLogger(__name__)

def get_coordinates(location_name):
    # Open-mateo geocoding REST API endpoint
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"

    # query parameters sent with the url
    params = {
        "name": location_name,
        "count": 1, #limits results to 1 match
        "language": "en",
        "format": "json"
    }
    logger.info(f"Geocoding search query: '{location_name}'")

    try:
        #sends HTTP GET request to the Geocoding API
        response = requests.get(geo_url,params=params)
        response.raise_for_status() #checks web service errors
        data = response.json()

        # verifies if any search results were returned
        if "results" in data and len(data["results"])>0:
            result = data["results"][0] #takes top match
            lat = result['latitude']
            lon = result['longitude']
            #format clean string(eg:'Kalanki,Nepal')
            formatted_name = f"{result['name']},{result.get('country','')}"
            logger.info(f"Found coordinates for {formatted_name}: ({lat}, {lon})")
            return lat,lon,formatted_name
        else:
            logger.warning(f"Location '{location_name}' not found.")
            return None, None, None

    except requests.exceptions.RequestException as e:
        logger.error(f"Geocoding API Connection Error: {e}")
        return None,None,None