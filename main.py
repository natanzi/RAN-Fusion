import os
import time
from multiprocessing import Process
from network.initialize_network import initialize_network
from Config_files.config_load import load_all_configs
from database.database_manager import DatabaseManager

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
                'data_size': data_size,
                # Add other relevant data fields here
            }

            # Log the data to the database
            db_manager.insert_ue_data(data)

            time.sleep(1)  # Logging interval

def main():
    # Load configurations
    base_dir = os.path.dirname(os.path.abspath(__file__))
    gNodeBs_config, cells_config, ue_config = load_all_configs(base_dir)

    # Specify the number of UEs to launch
    num_ues_to_launch = 50

    # Initialize gNodeBs, Cells, and UEs
    gNodeBs, cells, ues = initialize_network(num_ues_to_launch, gNodeBs_config, cells_config, ue_config)

    # Initialize DatabaseManager
    db_manager = DatabaseManager()

    # Create a separate process for logging
    logging_process = Process(target=log_traffic, args=(ues, db_manager))
    logging_process.start()

    logging_process.join()

if __name__ == "__main__":
    main()
