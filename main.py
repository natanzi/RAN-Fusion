import os
import time
from multiprocessing import Process
from network.initialize_network import initialize_network
from Config_files.config_load import load_all_configs
from database.database_manager import DatabaseManager
import logging
from logo import create_logo

logo_text = create_logo()
print("Printing logo start")
print(logo_text)
print("Printing logo end")

# At the beginning of your script
logging.basicConfig(level=logging.INFO)

# Check database connection
# Create an instance of DatabaseManager
db_manager = DatabaseManager()
connection_status = db_manager.check_database_connection()

def log_traffic(ues, db_manager):
    while True:
        for ue in ues:
            data_size, interval = ue.generate_traffic()
            print(f"UE ID: {ue.ID}, IMEI: {ue.IMEI}, Service Type: {ue.ServiceType}, Data Size: {data_size}, Interval: {interval} sec")
            
            # Prepare data for logging to the database
            data = {
                'ue_id': ue.ID,
                'imei': ue.IMEI,
                'service_type': ue.ServiceType,
                'data_size': float(data_size),
                # Add other relevant data fields here
            }
            # Log the data to the database
            db_manager.insert_ue_data(data)

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
    gNodeBs, cells, ues = initialize_network(num_ues_to_launch, gNodeBs_config, cells_config, ue_config)
    print(f"Number of UEs returned: {len(ues)}")

    time.sleep(2)
    # Initialize DatabaseManager
    db_manager = DatabaseManager()

    # Create a separate process for logging
    logging_process = Process(target=log_traffic, args=(ues, db_manager))
    logging_process.start()

    # Create a separate process for monitoring cell load
    cell_monitor_process = Process(target=monitor_cell_load, args=(gNodeBs,))
    cell_monitor_process.start()

    # Wait for the processes to complete
    logging_process.join()
    cell_monitor_process.join()

if __name__ == "__main__":
    main()