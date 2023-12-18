#time_utils.py located in database\time_utils.py
import asyncio
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

server_pools = [
    ["pool1.ntp.org", "time1.google.com"],
    ["pool2.ntp.org", "time2.facebook.com"]
]

async def get_ntp_time(server):
    try:
        ntp_client = ntplib.NTPClient()
        response = await asyncio.to_thread(ntp_client.request, server, timeout=5, version=3)
        utc_time = datetime.utcfromtimestamp(response.tx_time)
        est = pytz.timezone('US/Eastern')
        est_time = utc_time.replace(tzinfo=pytz.utc).astimezone(est)
        return est_time.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        logger.error(f"Error fetching time from NTP server '{server}': {e}")
        return None

async def get_current_time_ntp(server_pools, cache_expiry=CACHE_EXPIRY):
    global CACHED_TIME

    if CACHED_TIME and (default_time() - CACHED_TIME[1]) < cache_expiry:
        return CACHED_TIME[0]

    for pool in server_pools:
        for server in pool:
            est_time = await get_ntp_time(server)
            if est_time:
                CACHED_TIME = (est_time, default_time())
                return est_time
        await asyncio.sleep(1)  # Non-blocking sleep

    logger.error("All NTP pools failed! Returning system default time")
    return datetime.now(pytz.timezone('US/Eastern')).strftime("%Y-%m-%d %H:%M:%S")

if __name__ == "__main__":
    asyncio.run(get_current_time_ntp(server_pools))

