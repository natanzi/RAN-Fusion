import os
import logging
from Config_files.config import Config
from logo import create_logo
from database.database_manager import DatabaseManager
from network.initialize_network import initialize_network
from network.init_ue import initialize_ues
import time
from flask import Flask, websocket
import threading

app = Flask(__name__)
@websocket.route('/ues')
def home():
    while True:  
        websocket.sleep(1)
        
def monitor_network_changes():
    while True:
        # Logic to check for changes in the network state
        # For example, you might check a global variable or a database for updates
        # If there are changes, print them
        time.sleep(1)  # Adjust the sleep time as needed

# Start the monitoring thread
monitor_thread = threading.Thread(target=monitor_network_changes)
monitor_thread.daemon = True  # Daemonize thread
monitor_thread.start()

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


if __name__ == "__main__":
    main()