import requests
import logging

logger = logging.getLogger(__name__)

def send_notification(message_text):
    ntfy_topic = "idyllic-weather-alerts-006"
    ntfy_url = f"https://ntfy.sh/{ntfy_topic}"

    logger.info("Dispatching push alerts to ntfy server . . . ")

    try:
        response = requests.post(
            ntfy_url,
            data=message_text,
            headers={
                "Title": "Daily Weather and AQI Updtae",
                "Priority": "default",
                "Tags": "sun_behind_cloud, mask"
            }
        )
        response.raise_for_status()
        logger.info("Push notification dispatched successfully!")
        return True

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to sent ntfy push notification: {e}")
        return False