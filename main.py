import os
import logging
from Config_files.config import Config
from logo import create_logo
from database.database_manager import DatabaseManager
from network.initialize_network import initialize_network
from traffic.traffic_generator import TrafficController
from network.ue_manager import UEManager
from network.gNodeB_manager import gNodeBManager
import time
import threading
import queue

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

def log_traffic(ues, command_queue):
    # Initialize the TrafficController inside the child process
    traffic_controller = TrafficController(command_queue)
    while True:
        if not command_queue.empty():
            command = command_queue.get()
            if command == 'restart':
                logging.info("Received restart command. Reinitializing traffic generation with updated parameters.")
                # Use the get_updated_ues method to update the UEs
                ues = traffic_controller.get_updated_ues()
                continue
        # Generate traffic using the traffic_controller
        for ue in ues:
            # Assuming generate_traffic is a method of TrafficController that simulates traffic for a UE
            traffic_data = traffic_controller.generate_traffic(ue)
            # Log the traffic details in the desired format, including delay, jitter, and packet loss rate
            logging.info(f"UE ID: {ue.ID}, IMEI: {ue.IMEI}, Service Type: {ue.ServiceType}, Data Size: {traffic_data['data_size']:.2f}MB, Interval: {traffic_data['interval']:.2f}s, Delay: {traffic_data['ue_delay']}ms, Jitter: {traffic_data['ue_jitter']}ms, Packet Loss Rate: {traffic_data['ue_packet_loss_rate']}%")
        
        time.sleep(1)  # Logging interval

def main():

    logging.basicConfig(level=logging.INFO)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    logo_text = create_logo()
    print(logo_text)

    # Singleton instance of DatabaseManager is created here. This will be the same instance throughout the application.
    db_manager = DatabaseManager()
    time.sleep(1)

    # Call the new initialization function
    gNodeBs, cells, sectors, ues = initialize_network(base_dir, num_ues_to_launch=10)

    print("Network Initialization Complete")
    print(f" this is for debug and so Initialized sectors: {sectors}")  

    # Start monitoring UE operations in a separate thread
    threading.Thread(target=monitor_ue_updates, daemon=True).start()

    # Initialize command queue for traffic controller
    command_queue = queue.Queue()

    # Start traffic logging in a separate thread
    threading.Thread(target=log_traffic, args=(ues, command_queue), daemon=True).start()

    # Keep the main program running until manually stopped
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Program terminated by user.")

if __name__ == "__main__":
    main()