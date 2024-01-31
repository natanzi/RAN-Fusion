import os
import logging
from Config_files.config import Config  # Import the new Config class
from logo import create_logo
from database.database_manager import DatabaseManager
from network.initialize_network import initialize_network
from utills.debug_utils import debug_print
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
    gNodeBs, cells, sectors = initialize_network(base_dir)

    # Post-initialization steps, if any
    print("Network Initialization Complete")

    # Initialize UEs
    #num_ues_to_launch = 271  # This value should be set according to your needs
    #ues = initialize_ues(num_ues_to_launch, gNodeBs, sectors, config.ue_config, db_manager)
    #ues = initialize_ues(num_ues_to_launch, sectors, cells, gNodeBs, config.ue_config)

    #print("Initialized UEs:")

    #for ue in ues:
        #print(f"UE ID: {ue.ID}, Service Type: {ue.ServiceType}, Sector ID: {ue.ConnectedSector}, Cell ID: {ue.ConnectedCellID}, gNodeB ID: {ue.gNodeB_ID}")


if __name__ == "__main__":
    main()