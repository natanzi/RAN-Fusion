# external_latency_app.py
import time
from apscheduler.schedulers.background import BackgroundScheduler
from network_metrics import simulate_latency

# Assuming you have a way to get the current UE and gNodeBs data
def get_current_network_data():
    # This function should interface with your main simulation to get the current data
    pass

def update_latency():
    ue, gnodebs, service_type = get_current_network_data()
    latency = simulate_latency(ue, gnodebs, service_type)
    # Now, update the latency in your main simulation
    # This could be through an API call, database update, etc.
    pass

scheduler = BackgroundScheduler()
scheduler.add_job(update_latency, 'interval', seconds=10)  # Adjust the interval as needed
scheduler.start()

try:
    # Keep the script running
    while True:
        time.sleep(1)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()