#time_utils.py
# time_utils.py
import ntplib
from time import ctime
from datetime import datetime

def get_current_time_ntp(server='pool.ntp.org'):
    """Fetches current time from NTP server."""
    try:
        ntp_client = ntplib.NTPClient()
        response = ntp_client.request(server)
        timestamp = datetime.strptime(ctime(response.tx_time), "%a %b %d %H:%M:%S %Y").strftime("%Y-%m-%d %H:%M:%S")
        return timestamp
    except Exception as e:
        print("Error fetching time from NTP server:", e)
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Fallback to system time
