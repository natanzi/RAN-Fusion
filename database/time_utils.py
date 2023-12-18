#time_utils.py located in database\time_utils.py
import ntplib
import logging
from datetime import datetime
import pytz

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_current_time_ntp(server='pool.ntp.org'):
    """Fetches current time from NTP server and converts it to EST."""
    try:
        ntp_client = ntplib.NTPClient()
        response = ntp_client.request(server)
        utc_time = datetime.utcfromtimestamp(response.tx_time)

        # Convert UTC time to EST
        est = pytz.timezone('US/Eastern')
        est_time = utc_time.replace(tzinfo=pytz.utc).astimezone(est)
        return est_time.strftime("%Y-%m-%d %H:%M:%S")
    except ntplib.NTPException as e:
        logger.error(f"Error fetching time from NTP server: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

    # Fallback to system time in EST
    est = pytz.timezone('US/Eastern')
    return datetime.now(est).strftime("%Y-%m-%d %H:%M:%S")

# Example usage
if __name__ == "__main__":
    current_time = get_current_time_ntp()
    print(f"Current Time: {current_time}")
