import os
import logging
import time
import signal
import multiprocessing
from multiprocessing import Queue
from Config_files.config import Config
from logo import create_logo
from database.database_manager import DatabaseManager
from network.initialize_network import initialize_network
from traffic.traffic_generator import TrafficController
from network.ue_manager import UEManager
from network.gNodeB_manager import gNodeBManager
from network.cell_manager import CellManager
from network.sector_manager import SectorManager
from network.NetworkLoadManager import NetworkLoadManager
from logs.logger_config import gnodbe_load_logger, ue_logger
from network.network_delay import NetworkDelay
from simulator_cli import SimulatorCLI
from threading import Thread
from API_Gateway import API

def run_api(queue):
    # Example of using the queue within the API process if needed
    # This is a placeholder for where you might handle incoming queue messages
    while True:
        message = queue.get()  # This will block until an item is available
        if message == "SHUTDOWN":
            print("Shutting down API server...")
            break
        # Handle other messages or perform actions based on the queue content
    API.app.run(port=5000)

def generate_traffic_loop(traffic_controller, ue_list, network_load_manager, network_delay_calculator, db_manager):
    while True:
        for ue in ue_list:
            throughput_data = traffic_controller.calculate_throughput(ue)
            network_load = network_load_manager.calculate_network_load()
            network_delay = network_delay_calculator.calculate_delay(network_load)
            db_manager.write_network_measurement(network_load, network_delay)
        time.sleep(1)

def main():
    logging.basicConfig(level=logging.INFO)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    logo_text = create_logo()
    print(logo_text)
    db_manager = DatabaseManager.get_instance()
    if db_manager.test_connection():
        print("Connection to InfluxDB successful.")
    else:
        print("Failed to connect to InfluxDB. Exiting...")
        return
    
    time.sleep(1)
    
    gNodeB_manager = gNodeBManager.get_instance(base_dir=base_dir)
    gNodeBs, cells, sectors, ues, cell_manager = initialize_network(base_dir, num_ues_to_launch=10)
    print("Network Initialization Complete")
    
    sector_manager = SectorManager.get_instance(db_manager=db_manager)
    network_load_manager = NetworkLoadManager.get_instance(cell_manager, sector_manager)
    network_load_manager.log_and_write_loads()
    ue_manager = UEManager.get_instance(base_dir)  
    network_delay_calculator = NetworkDelay()
    
    traffic_controller_instance = TrafficController()
    traffic_thread = Thread(target=generate_traffic_loop, args=(traffic_controller_instance, ues, network_load_manager, network_delay_calculator, db_manager))
    traffic_thread.start()
    
    cli = SimulatorCLI(gNodeB_manager=gNodeB_manager, cell_manager=cell_manager, sector_manager=sector_manager, ue_manager=ue_manager, network_load_manager=network_load_manager, base_dir=base_dir)
    
    # Setup inter-process communication Queue
    ipc_queue = Queue()
    api_proc = multiprocessing.Process(target=run_api, args=(ipc_queue,))
    api_proc.start()

    def signal_handler(signum, frame):
        print("Signal received, shutting down gracefully...")
        ipc_queue.put("SHUTDOWN")  # Signal the API process to shutdown
        api_proc.join()  # Wait for the API process to exit
        print("API server shutdown complete.")
        traffic_thread.join()  # Ensure the traffic generation thread is also cleanly shutdown
        exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    cli.cmdloop()

if __name__ == "__main__":
    main()