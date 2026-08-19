#IMPORTING
import json
import os
import logging

#create logger instance
logger = logging.getLogger(__name__)

config_file = "config.json"

def load_saved_location():
    if os.path.exists(config_file):
        try:
            with open(config_file,'r') as f:
                data = json.load(f)
                logger.info(f"Loaded configuration for '{data['location']}'")
                return data['longitude'], data['latitude'], data['location']
        except Exception as e:
            logger.warning(f"Error: Could not read config file: {e}")
            return None, None, None
    logger.info("No config.json file found on disk.")
    return None ,None,None

def save_location(latitude, longitude, location):
    data={
        'latitude': latitude,
        'longitude': longitude,
        'location': location

    }
    try:
        with open(config_file,'w') as f:
            json.dump(data,f,indent=3)
        logger.info(f"Saved location '{location}' to config.json")
        print(f"Saved {location} as your location.")
    except Exception as e:
        logger.error(f"Failed to save location to disk: {e}")


 



