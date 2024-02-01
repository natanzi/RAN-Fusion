import os
import logging
from Config_files.config import Config
from logo import create_logo
from database.database_manager import DatabaseManager
from network.initialize_network import initialize_network
from network.init_ue import initialize_ues
import time
import threading

        
def monitor_ue_updates():
    log_file_path = 'ue_updates.log'
    # Ensure the file exists, create if it doesn't
    open(log_file_path, 'a').close()
    with open(log_file_path, 'r') as file:
        # Move to the end of the file
        file.seek(0,2)
        while True:
            line = file.readline()
            if not line:
                time.sleep(0.1)  # Sleep briefly to avoid busy waiting
                continue
            print(line.strip(), flush=True)

def main():

    logging.basicConfig(level=logging.INFO)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    logo_text = create_logo()
    print(logo_text)

    # Create an instance of DatabaseManager here
    db_manager = DatabaseManager()
    
    #sleep
    time.sleep(1)

    # Call the new initialization function
    gNodeBs, cells, sectors, ues = initialize_network(base_dir, num_ues_to_launch=10)
    
        # Post-initialization steps, if any
    print("Network Initialization Complete")

    # Start monitoring UE operations in a separate thread
    threading.Thread(target=monitor_ue_updates, daemon=True).start()

    # Keep the main program running until manually stopped
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Program terminated by user.")

if __name__ == "__main__":
    main()