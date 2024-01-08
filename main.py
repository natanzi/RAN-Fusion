import os
import time
from multiprocessing import Process, Queue, Manager
from network.initialize_network import initialize_network
from Config_files.config_load import load_all_configs
import logging
from logo import create_logo
from health_check.do_health_check import perform_health_check
from network.network_state import NetworkState
from network.handover_utils import handle_load_balancing, monitor_and_log_cell_load
from health_check.system_monitoring import SystemMonitor
from database.database_manager import DatabaseManager
from logs.logger_config import traffic_update
import threading
from traffic.traffic_generator import TrafficController
from network.init_sector import initialize_sectors
from network.gNodeB import gNodeB, load_gNodeB_config

#################################################################################################################################
# pickled by multiprocessing
def log_system_resources(system_monitor, manager):
    while True:
        system_monitor.log_resource_usage()
        time.sleep(5)  
    manager.shutdown()

def network_state_manager(network_state, command_queue):
    while True:
        command = command_queue.get()  # Retrieve the command from the queue
        if command == 'save':
            network_state.save_state_to_influxdb()
        elif command == 'exit':  # Handle exit command to break the loop
            break
def create_shared_network_state(manager):
    # Create a proxy NetworkState object using the Manager
    network_state = manager.Namespace()
    # Initialize the NetworkState properties within the proxy object
    network_state.gNodeBs = manager.dict()
    network_state.cells = manager.dict()
    network_state.ues = manager.dict()
    network_state.last_update = manager.Value('i', time.time())
    return network_state  
#####################################################################################################################################
def log_traffic(ues, command_queue, network_state):
    traffic_controller = TrafficController(command_queue)
    updated_ue_ids = set()  # Keep track of updated UE IDs

    while True:
        # Log to confirm the loop is running
        logging.debug("Starting traffic logging loop iteration.")

        for ue in ues:
            # Calculate throughput instead of generating traffic
            throughput_data = traffic_controller.calculate_and_write_ue_throughput(ue)

            # Extract the required values from the traffic_data dictionary
            delay = throughput_data['delay']
            jitter = throughput_data['jitter']
            packet_loss_rate = throughput_data['packet_loss_rate']
            formatted_throughput = f"{throughput_data['throughput']:.2f}"

            # Check if the UE has been updated and change the log color to red
            log_color = "\033[91m" if ue.ID in updated_ue_ids else "\033[0m"

            logging.info(
                f"{log_color}UE ID: {ue.ID}, Service Type: {ue.ServiceType}, Throughput: {formatted_throughput}Mbps, "
                f"Interval: {throughput_data['interval']}s, Delay: {delay}ms, Jitter: {jitter}ms, "
                f"Packet Loss Rate: {packet_loss_rate}%\033[0m"
            )

        # Check for new commands and apply updates if necessary
        if not command_queue.empty():
            command = command_queue.get()
            logging.debug(f"Processing command: {command}")
            # Log the received command
            logging.debug(f"Received command from queue: {command}")

            if command['type'] == 'update':
                logging.info(f"Received update for {command['service_type']} traffic. Updating parameters. Update ID: {command['update_id']}")
                traffic_controller.update_parameters(command['data'])

                # Log the updated_ue_ids set before the update
                logging.debug(f"Updated UE IDs before update: {updated_ue_ids}")

                # Call get_updated_ues to apply the updates to the UEs
                updated_ues = traffic_controller.get_updated_ues()

                # Apply the update for matching UEs and add their IDs to the updated_ue_ids set
                for ue in updated_ues:
                    if ue.ServiceType.lower() == command['service_type'].lower():
                        updated_ue_ids.add(ue.ID)
                        updated_traffic = traffic_controller.generate_updated_traffic(ue)
                        logging.getLogger('traffic_update').info(
                            f"\033[91mUE ID: {ue.ID} - Updated {ue.ServiceType} traffic with parameters: {command['data']} (Update ID: {command['update_id']})\033[0m"
                        )

                # Log the updated_ue_ids set after the update
                logging.debug(f"Updated UE IDs after update: {updated_ue_ids}")

            elif command['type'] == 'save':
                network_state.save_state_to_influxdb()
            elif command['type'] == 'exit':
                # Log the exit command before breaking the loop
                logging.debug("Received 'exit' command. Exiting traffic logging loop.")
                break

        # Sleep for a second before the next iteration
        time.sleep(1)
#####################################################################################
def main():
    logo_text = create_logo()
    print(logo_text)
    logging.basicConfig(level=logging.INFO)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    gNodeBs_config, cells_config, ue_config, sectors_config = load_all_configs(base_dir)
    
    # Initialize the Manager
    manager = Manager()
    shared_network_state = create_shared_network_state(manager)
    
    # Pass the proxy network_state to the NetworkState instance
    network_state = NetworkState(shared_network_state)
    db_manager = DatabaseManager(network_state)
    
    if perform_health_check(network_state):
        print("Health check passed.")
    else:
        print("Health check failed.")
        return  # Exit if health check fails
    
    num_ues_to_launch = 10
    # Initialize gNodeBs, cells, and UEs
    gNodeBs, cells, ues = initialize_network(num_ues_to_launch, gNodeBs_config, cells_config, ue_config, db_manager)
    print(f"Number of UEs returned: {len(ues)}")
    time.sleep(2)
    
    command_queue = Queue()
    # Create an instance of TrafficController and pass the command_queue
    traffic_controller = TrafficController(command_queue)
    
    # Start the network state manager process
    logging_process = Process(target=log_traffic, args=(network_state.serialize_for_logging(), command_queue))
    logging_process.start()

    
    # Start the cell monitor threads using monitor_and_log_cell_load
    #for gNodeB_instance in gNodeBs.values():
        #cell_load_thread = threading.Thread(target=monitor_and_log_cell_load, args=(gNodeB_instance, traffic_controller))
        #cell_load_thread.daemon = True  # This ensures the thread will exit when the main program does
        #cell_load_thread.start()
    
    # Instantiate the SystemMonitor
    system_monitor = SystemMonitor(network_state)
    
    # Start the system resource logging process with system_monitor passed as an argument
    system_resource_logging_process = Process(target=log_system_resources, args=(system_monitor,))
    system_resource_logging_process.start()
    
    # Start the congestion detection process using monitor_and_log_cell_load
    # Make sure to pass a serializable object or reconstruct the gNodeB objects within the child process
    congestion_process = Process(target=monitor_and_log_cell_load, args=(shared_network_state.gNodeBs, traffic_controller))


    try:
        congestion_process.start()
    except Exception as e:
        logging.error(f"Failed to start congestion_process: {e}")
    
    # Start the network state manager process
    ns_manager_process = Process(target=network_state_manager, args=(network_state, command_queue))
    ns_manager_process.start()
    
    # Wait for the processes to complete (if they ever complete)
    logging_process.join()
    congestion_process.join()
    system_resource_logging_process.join()
    
    # Signal the network state manager process to exit
    command_queue.put('exit')
    ns_manager_process.join()

if __name__ == "__main__":
    main()