import os
import time
from multiprocessing import Process
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

# Create an instance of NetworkState
network_state = NetworkState()
# Initialize DatabaseManager with network_state
db_manager = DatabaseManager(network_state)

# Pass network_state to perform_health_check
if perform_health_check(network_state):
    print("Health check passed.")
else:
    print("Health check failed.")

# At the beginning of your script
logging.basicConfig(level=logging.INFO)

def log_traffic(ues, traffic_increase_config=None):
    # Initialize DatabaseManager inside the function
    network_state = NetworkState()
    db_manager = DatabaseManager(network_state)
    
    while True:
        for ue in ues:
            # Check if this UE should have increased traffic
            if traffic_increase_config and ue.ID in traffic_increase_config:
                # Get the traffic increase factor for this UE
                traffic_multiplier = traffic_increase_config[ue.ID]
            else:
                # Default traffic multiplier is 1 (no increase)
                traffic_multiplier = 1

            # Generate traffic with the potential multiplier
            data_size, interval = ue.generate_traffic()
            data_size *= traffic_multiplier  # Apply the traffic multiplier

            print(f"UE ID: {ue.ID}, IMEI: {ue.IMEI}, Service Type: {ue.ServiceType}, Data Size: {data_size}, Interval: {interval} sec")
            
            # Prepare data for logging to the database
            data = {
                'ue_id': ue.ID,
                'imei': ue.IMEI,
                'service_type': ue.ServiceType,
                'data_size': float(data_size),
                # Add other relevant data fields here
            }
            point = ue.serialize_for_influxdb()
            db_manager.insert_data(point)  # Use the correct method here

            time.sleep(1)  # Logging interval

def monitor_cell_load(gNodeBs):
    while True:
        for gNodeB_id, gNodeB_instance in gNodeBs.items():  # Iterate over the dictionary items
            gNodeB_instance.update()  # Call the update method for each gNodeB instance
        time.sleep(5)  # Adjust the sleep time as needed for your simulation

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    gNodeBs_config, cells_config, ue_config = load_all_configs(base_dir)

    # Specify the number of UEs to launch
    num_ues_to_launch = 40

    # Initialize gNodeBs, Cells, and UEs
    gNodeBs, cells, ues = initialize_network(num_ues_to_launch, gNodeBs_config, cells_config, ue_config, db_manager)

    print(f"Number of UEs returned: {len(ues)}")
    time.sleep(2)
    # The DatabaseManager has already been initialized with network_state at the beginning of the script
    # So we don't need to initialize it again here

    # Example traffic increase configuration
    # This can be modified or managed through a GUI or API endpoint
    traffic_increase_config = {1: 2, 3: 1.5}

    # Create a separate process for logging without passing db_manager
    logging_process = Process(target=log_traffic, args=(ues, traffic_increase_config))
    logging_process.start()

    # Create a separate process for monitoring cell load
    cell_monitor_process = Process(target=monitor_cell_load, args=(gNodeBs,))
    cell_monitor_process.start()

    # Wait for the processes to complete
    logging_process.join()
    cell_monitor_process.join()

if __name__ == "__main__":
    main()