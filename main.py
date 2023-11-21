import os
import time
from multiprocessing import Process
from network.initialize_network import initialize_network
from Config_files.config_load import load_all_configs
from visualization.plot_network import plot_network
import matplotlib
matplotlib.use('Agg')  # Set a non-interactive backend

def visualize_network(gNodeBs, ues):
    while True:
        plot_network(gNodeBs, ues, show_cells=True, background_image_path='images/worcester_map.jpg')
        time.sleep(10)  # Update interval for the visualization

def log_traffic(ues):
    while True:
        for ue in ues:
            data_size, interval = ue.generate_traffic()
            print(f"UE ID: {ue.ID}, Service Type: {ue.ServiceType}, Data Size: {data_size} KB/MB, Interval: {interval} sec")
        time.sleep(1)  # Logging interval

def main():
    # Load configurations
    base_dir = os.path.dirname(os.path.abspath(__file__))
    gNodeBs_config, cells_config, ue_config = load_all_configs(base_dir)

    # Specify the number of UEs to launch
    num_ues_to_launch = 50

    # Initialize gNodeBs, Cells, and UEs
    gNodeBs, cells, ues = initialize_network(num_ues_to_launch)
    
    # Create a separate process for visualization
    visualization_process = Process(target=visualize_network, args=(gNodeBs, ues))
    visualization_process.start()

    # Create a separate process for logging
    logging_process = Process(target=log_traffic, args=(ues,))
    logging_process.start()

    # Wait for the processes to complete (they won't in this case since they run indefinitely)
    visualization_process.join()
    logging_process.join()

if __name__ == "__main__":
    main()

