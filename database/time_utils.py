#time_utils.py located in database\time_utils.py
import ntplib
import logging
from datetime import datetime
import pytz
from time import monotonic as default_time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CACHED_TIME = None
CACHE_EXPIRY = 30 * 60  # 30 minutes
RETRY_LIMIT = 3  # Number of retries for each NTP server

server_pools = [
    "pool1.ntp.org", 
    "time1.google.com", 
    "pool2.ntp.org", 
    "time2.facebook.com"
]

def is_time_valid(time_to_check):
    """Validate the received time."""
    # Implement logic to validate the time
    # For simplicity, we'll assume the time is valid if it's not None
    return time_to_check is not None

def get_current_time_ntp(cache_expiry=CACHE_EXPIRY):
    global CACHED_TIME

    if CACHED_TIME and (default_time() - CACHED_TIME[1]) < cache_expiry:
        return CACHED_TIME[0]

    ntp_client = ntplib.NTPClient()
    for server in server_pools:
        for _ in range(RETRY_LIMIT):
            try:
                response = ntp_client.request(server, timeout=5, version=3)
                utc_time = datetime.utcfromtimestamp(response.tx_time)
                
                est = pytz.timezone('US/Eastern')
                est_time = utc_time.replace(tzinfo=pytz.utc).astimezone(est)
                formatted_time = est_time.strftime("%Y-%m-%d %H:%M:%S")

                if is_time_valid(formatted_time):
                    CACHED_TIME = (formatted_time, default_time())
                    return formatted_time

            except Exception as e:
                logger.error(f"Attempt to fetch time from NTP server '{server}' failed: {e}")
                continue  # Retry

    logger.error("All NTP pools failed! Returning system default time")
    return datetime.now(pytz.timezone('US/Eastern')).strftime("%Y-%m-%d %H:%M:%S")

if __name__ == "__main__":
    current_time = get_current_time_ntp()
    print(f"Current Time: {current_time}")

