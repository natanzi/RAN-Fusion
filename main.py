import os
import logging
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
from logs.logger_config import gnodbe_load_logger
from network.network_delay import NetworkDelay
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

def log_traffic(ues, network_load_manager):

    # Initialize the TrafficController inside the child process
    traffic_controller = TrafficController()
    network_delay_calculator = NetworkDelay()

    while True:
        # Generate traffic using the traffic_controller
        for ue in ues:
            # Calculate throughput for the UE
            throughput_data = traffic_controller.calculate_throughput(ue)
            network_load = network_load_manager.calculate_network_load()
            network_delay = network_delay_calculator.calculate_delay(network_load)

            # Log the traffic details in the desired format, including throughput, delay, jitter, and packet loss rate
            logging.info(f"UE ID: {ue.ID}, Service Type: {ue.ServiceType}, Throughput: {throughput_data['throughput'] / (8 * 1024 * 1024):.2f}MB, Interval: {throughput_data['interval']:.2f}s, Delay: {throughput_data['jitter']}ms, Jitter: {throughput_data['packet_loss_rate']}%, Packet Loss Rate: {throughput_data['packet_loss_rate']}%")

        
        time.sleep(1)  # Logging interval

def main():
    logging.basicConfig(level=logging.INFO)
    base_dir = os.path.dirname(os.path.abspath(__file__))

    logo_text = create_logo()
    print(logo_text)

    db_manager = DatabaseManager()
    time.sleep(1)

    gNodeBs, cells, sectors, ues = initialize_network(base_dir, num_ues_to_launch=10)
    print("Network Initialization Complete")
    print(f" this is for debug and so Initialized sectors: {sectors}")

    # Correctly initialize CellManager
    cell_manager = CellManager(gNodeBs=gNodeBs, db_manager=db_manager)

    # Correctly initialize SectorManager without the 'sectors' keyword argument
    sector_manager = SectorManager(db_manager=db_manager)

    # Initialize NetworkLoadManager with the cell and sector managers
    network_load_manager = NetworkLoadManager(cell_manager, sector_manager)

    # Calculate and log the network load
    network_load_manager.log_and_write_loads()

    # Initialize NetworkDelay
    network_delay_calculator = NetworkDelay()

    # Calculate and log the gNodeB loads
    gNodeB_loads = network_load_manager.calculate_gNodeB_load()
    for gNodeB_id, load in gNodeB_loads.items():
        gnodbe_load_logger.info(f"gNodeB {gNodeB_id} Load: {load:.2f}%")

    # New code to calculate cell load and serialize for InfluxDB
    for cell_id, cell in cell_manager.cells.items():
        cell_load = network_load_manager.calculate_cell_load(cell)  # Calculate the cell's load
        serialized_data = cell.serialize_for_influxdb(cell_load)  # Serialize cell data with load for InfluxDB
        # Here you would typically send serialized_data to InfluxDB or log it
        print(f"Serialized data for cell {cell_id}: {serialized_data.to_line_protocol()}")

    threading.Thread(target=log_traffic, args=(ues, network_load_manager), daemon=True).start()

    # Keep the main program running until manually stopped
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Program terminated by user.")

if __name__ == "__main__":
    main()