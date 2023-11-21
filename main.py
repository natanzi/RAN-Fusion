import os
import time
from network.initialize_network import initialize_network
from Config_files.config_load import load_all_configs
from visualization.plot_network import plot_network

def main():
    # Load configurations
    base_dir = os.path.dirname(os.path.abspath(__file__))
    gNodeBs_config, cells_config, ue_config = load_all_configs(base_dir)

    # Specify the number of UEs to launch
    num_ues_to_launch = 50

    # Initialize gNodeBs, Cells, and UEs
    gNodeBs, cells, ues = initialize_network(num_ues_to_launch)
    
    # Initialize visualization
    plot_network(gNodeBs, ues, show_cells=True, background_image_path='images/worcester_map.jpg')

    # Run the simulation indefinitely
    while True:
        for ue in ues:
            data_size, interval = ue.generate_traffic()
            print(f"UE ID: {ue.ID}, Service Type: {ue.ServiceType}, Data Size: {data_size} KB/MB, Interval: {interval} sec")
        
        # Update the visualization at a specified interval (e.g., every 10 seconds)
        time.sleep(10)
        plot_network(gNodeBs, ues, show_cells=True, background_image_path='images/worcester_map.jpg')

if __name__ == "__main__":
    main()

