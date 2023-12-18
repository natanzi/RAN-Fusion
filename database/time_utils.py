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
CACHE_EXPIRY = 30 * 60 # 30 minutes

server_pools = [
["pool1.ntp.org", "time1.google.com"],
["pool2.ntp.org", "time2.facebook.com"] 
]

def get_current_time_ntp(server_pools, cache_expiry=CACHE_EXPIRY):

    global CACHED_TIME

    if CACHED_TIME and (default_time() - CACHED_TIME[1]) < cache_expiry:
        return CACHED_TIME[0]  

    for pool in server_pools:
        for server in pool:
            try:
                ntp_client = ntplib.NTPClient()
                response = ntp_client.request(server, timeout=5, version=3)  
                utc_time = datetime.utcfromtimestamp(response.tx_time)
        
                est = pytz.timezone('US/Eastern')
                est_time = utc_time.replace(tzinfo=pytz.utc).astimezone(est)

                CACHED_TIME = (est_time.strftime("%Y-%m-%d %H:%M:%S"), default_time()) 
                return CACHED_TIME[0]
        
            except ntplib.NTPException as e:
                logger.error(f"Failed reaching {server}, trying next server")
            except Exception as e:
                logger.error(f"Unexpected error with {server}")
    
        # Sleep before trying next pool 
        time.sleep(1)

    logger.error("All NTP pools failed! Returning system default time")  
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if __name__ == "__main__":

    current_time = get_current_time_ntp(server_pools)
    print(f"Current Time: {current_time}")
