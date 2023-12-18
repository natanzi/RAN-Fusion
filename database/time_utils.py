#time_utils.py located in database\time_utils.py
import ntplib
import logging
from datetime import datetime
import pytz

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_current_time_ntp(servers=['pool.ntp.org', 'time.google.com', 'time.windows.com'], timeout=5):
    """Fetches current time from a list of NTP servers and converts it to EST."""
    for server in servers:
        try:
            ntp_client = ntplib.NTPClient()
            response = ntp_client.request(server, timeout=timeout)
            utc_time = datetime.utcfromtimestamp(response.tx_time)

            est = pytz.timezone('US/Eastern')
            est_time = utc_time.replace(tzinfo=pytz.utc).astimezone(est)
            return est_time.strftime("%Y-%m-%d %H:%M:%S")
        except ntplib.NTPException as e:
            logger.error(f"Error fetching time from NTP server '{server}': {e}")
        except Exception as e:
            logger.error(f"Unexpected error with server '{server}': {e}")

    # Fallback to system time in EST
    logger.warning("Falling back to system time in EST")
    est = pytz.timezone('US/Eastern')
    return datetime.now(est).strftime("%Y-%m-%d %H:%M:%S")

if __name__ == "__main__":
    current_time = get_current_time_ntp()
    print(f"Current Time: {current_time}")
