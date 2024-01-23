import os
import time
import logging
import threading
from multiprocessing import Process, Queue
from Config_files.config_load import load_all_configs
from logo import create_logo
from health_check.do_health_check import perform_health_check
from network.initialize_network import initialize_network
from network.init_gNodeB import initialize_gNodeBs
from network.init_cell import initialize_cells
from network.init_sector import initialize_sectors
from network.init_ue import initialize_ues
from traffic.traffic_generator import TrafficController
#####################################################################################################################################
def log_traffic(ues, command_queue, gNodeBs):
    traffic_controller = TrafficController(command_queue)
    while True:
        print("Debug: log_traffic loop running.")
        for ue in ues:
            gnodeb = gNodeBs.get(ue.gNodeB_ID, None)
            if gnodeb is None:
                logging.error(f"gNodeB instance for UE ID {ue.ID} not found.")
                continue
            throughput_data = traffic_controller.calculate_and_write_ue_throughput(ue, gnodeb)
            try:
                formatted_throughput = f"{float(throughput_data['throughput']):.2f}"
                logging.info(
                    f"UE ID: {ue.ID}, Service Type: {ue.ServiceType}, Throughput: {formatted_throughput} Mbps, "
                    f"Interval: {throughput_data['interval']}s, Application Delay: {throughput_data['application_delay']}ms, "
                    f"Network Delay: {throughput_data['network_delay']}ms, Jitter: {throughput_data['jitter']}ms, "
                    f"Packet Loss Rate: {throughput_data['packet_loss_rate']}%"
                )
            except ValueError:
                logging.error(f"Invalid throughput data: {throughput_data['throughput']}")
        time.sleep(1)
#####################################################################################################################################
def main():
    logo_text = create_logo()
    print(logo_text)
    logging.basicConfig(level=logging.INFO)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    gNodeBs_config, cells_config, ue_config = load_all_configs(base_dir)

    if perform_health_check():
        print("Health check passed.")
    else:
        print("Health check failed.")
        return

    num_ues_to_launch = 10
    gNodeBs = initialize_gNodeBs(gNodeBs_config)
    cells = initialize_cells(gNodeBs)
    sectors = initialize_sectors(cells)
    ues = initialize_ues(num_ues_to_launch, sectors, ue_config)

    command_queue = Queue()
    traffic_controller = TrafficController(command_queue)

    # Start the traffic logging process
    logging_process = Process(target=log_traffic, args=(ues, command_queue, gNodeBs))
    print("Debug: Starting traffic logging process.")
    logging_process.start()

    # Wait for the logging process to complete
    logging_process.join()

    # Signal the end of the simulation
    command_queue.put('exit')

if __name__ == "__main__":
    main()