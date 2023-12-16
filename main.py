import os
import time
from multiprocessing import Process, Manager
from network.initialize_network import initialize_network
from Config_files.config_load import load_all_configs
from database.database_manager import DatabaseManager
import logging
from logo import create_logo
from health_check.do_health_check import perform_health_check
from network.network_state import NetworkState

logo_text = create_logo()
print("Printing logo start")
print(logo_text)
print("Printing logo end")

# At the beginning of your script
logging.basicConfig(level=logging.INFO)

def log_traffic(ues, network_state, traffic_increase_config=None):
    while True:
        for ue in ues:
            # ... existing traffic logging logic ...

            # After updating the network state, save it to InfluxDB
            network_state.save_state_to_influxdb()
        time.sleep(1)  # Logging interval

def monitor_cell_load(gNodeBs, network_state):
    while True:
        for gNodeB_id, gNodeB_instance in gNodeBs.items():
            # ... existing cell monitoring logic ...

            # After updating the network state, save it to InfluxDB
            network_state.save_state_to_influxdb()
        time.sleep(5)  # Adjust the sleep time as needed for your simulation

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    gNodeBs_config, cells_config, ue_config = load_all_configs(base_dir)

    # Create an instance of NetworkState
    network_state = NetworkState()
    # Initialize DatabaseManager with network_state
    db_manager = DatabaseManager(network_state)

    # Pass network_state to perform_health_check
    if perform_health_check(network_state):
        print("Health check passed.")
    else:
        print("Health check failed.")

    # Specify the number of UEs to launch
    num_ues_to_launch = 40

    # Initialize gNodeBs, Cells, and UEs
    gNodeBs, cells, ues = initialize_network(num_ues_to_launch, gNodeBs_config, cells_config, ue_config, db_manager)

    print(f"Number of UEs returned: {len(ues)}")
    time.sleep(2)

    # Example traffic increase configuration
    traffic_increase_config = {1: 2, 3: 1.5}

    # Use Manager from multiprocessing to create a proxy for NetworkState
    manager = Manager()
    network_state_proxy = manager.Namespace()
    network_state_proxy.state = network_state

    # Create a separate process for logging
    logging_process = Process(target=log_traffic, args=(ues, network_state_proxy, traffic_increase_config))
    logging_process.start()

    # Create a separate process for monitoring cell load
    cell_monitor_process = Process(target=monitor_cell_load, args=(gNodeBs, network_state_proxy))
    cell_monitor_process.start()

    # Wait for the processes to complete
    logging_process.join()
    cell_monitor_process.join()

if __name__ == "__main__":
    main()