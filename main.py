import os
import logging
from Config_files.config import Config  # Import the new Config class
from logo import create_logo
from database.database_manager import DatabaseManager
from network.initialize_network import initialize_network
from utills.debug_utils import debug_print
from network.init_ue import initialize_ues

import time

def main():

    logging.basicConfig(level=logging.INFO)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    logo_text = create_logo()
    print(logo_text)

    # Create an instance of DatabaseManager here
    db_manager = DatabaseManager()
    
    #sleep
    time.sleep(3)

    # Call the new initialization function
    gNodeBs, cells, sectors, ues = initialize_network(base_dir, num_ues_to_launch=50)

    # Post-initialization steps, if any
    print("Network Initialization Complete")

if __name__ == "__main__":
    main()