import logging
import sys
import csv
from datetime import datetime  
import os 

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger("main")

# Import custom functions from our src/ package
from src.config_manager import load_saved_location, save_location
from src.geocoder import get_coordinates
from src.weather_service import fetch_weather_report
from src.notifier import send_notification


def run_pipeline():
    """Main function that connects and runs all project modules step-by-step."""
    
    logger.info("Starting Weather & AQI Notifier pipeline...")

    lat, lon, label = load_saved_location()

    is_automated = "--cron" in sys.argv

    if lat and lon:
        logger.info(f"Target location loaded: {label}")

        if not is_automated:
            print(f"\n Saved Location: {label}")
            print("1. Send Weather Report for Saved Location")
            print("2. Change Saved Location")
            
            # Ask the user what they want to do
            choice = input("Select an option (1 or 2): ").strip()
            
            # If the user wants to change location
            if choice == "2":
                new_location = input("Enter new city/neighborhood: ").replace(","," ").strip()
                
                # Get new coordinates from the geocoder module
                new_lat, new_lon, new_label = get_coordinates(new_location)
                
                # If new coordinates are found, update active values and save to file
                if new_lat and new_lon:
                    save_location(new_lat, new_lon, new_label)
                    lat, lon, label = new_lat, new_lon, new_label
    else:
        # Initial run setup if config.json is not found
        logger.info("No location found. Setting up location...")
        
        if not is_automated:
            # Prompt user to enter their city name
            location_input = input("Enter city/neighborhood (e.g. Kalanki): ").replace(","," ").strip()
            lat, lon, label = get_coordinates(location_input)

            if lat and lon:
                save_location(lat, lon, label)
        else:
            logger.warning("Automated execution missing config.json! Using default location.")
            lat, lon, label = 27.6939, 85.2817, "Kalanki, Kathmandu"
   
    if lat and lon:
        # Fetch weather and AQI string from Open-Meteo APIs
        report = fetch_weather_report(lat, lon, label)
        
        if report:
            # Display report in console
            print("\n---  GENERATED REPORT ---")
            print(report)
            
            # Send mobile push alert via ntfy.sh
            send_notification(report)

def log_weather_history(location, temp, humidity, condition):
    os.makedirs("data", exist_ok=True)
    file_path = "data/weather_history.csv"
    file_exists = os.path.isfile(file_path)

    with open(file_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Location", "Temperature_C", "Humidity_%", "Condition"])
        # Write daily entry
        writer.writerow([datetime.now().isoformat(), location, temp, humidity, condition])

if __name__ == "__main__":
    run_pipeline()

