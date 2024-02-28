#simulator_cli.py is located in root directory to allows you to type commands like ue-list to see the list of current UEs.
import cmd
import time
import textwrap
from functools import partial
from network.ue_manager import UEManager
from network.gNodeB_manager import gNodeBManager
from network.cell_manager import CellManager
from network.sector_manager import SectorManager
from prettytable import PrettyTable
from network.sector import Sector
from network.NetworkLoadManager import NetworkLoadManager
from traffic.traffic_generator import TrafficController
from threading import Thread, Event
import threading
import os
from network.ue import UE
from network.command_handler import CommandHandler
from colorama import Fore, Style, init

init(autoreset=True) 
# Define your aliases and commands in a more flexible structure
# For the purpose of this example, it's defined within the code, but it could be external
alias_config = {
    'aliases': [
        {'alias': 'gnb', 'command': 'gnb_list'},
        {'alias': 'cell', 'command': 'cell_list'},
        {'alias': 'sector', 'command': 'sector_list'},
        {'alias': 'ue', 'command': 'ue_list'},
        {'alias': 'ulog', 'command': 'ue_log'},
        # Add more aliases as needed
    ]
}

class SimulatorCLI(cmd.Cmd):
    def __init__(self, gNodeB_manager, cell_manager, sector_manager, ue_manager, network_load_manager, base_dir, *args, **kwargs):
        self.traffic_controller = TrafficController()
        self.base_dir = base_dir
        super().__init__(*args, **kwargs, completekey='tab')
        self.display_thread = None
        self.running = False  # Flag to control the display thread
        self.aliases = self.generate_alias_mappings(alias_config)
        self.gNodeB_manager = gNodeB_manager
        self.cell_manager = cell_manager
        self.sector_manager = sector_manager
        self.ue_manager = UEManager.get_instance(base_dir=self.base_dir)
        self.network_load_manager = network_load_manager
        self.stop_event = Event()

    @staticmethod
    def generate_alias_mappings(config):
        """Generates a dictionary mapping aliases to commands."""
        mappings = {}
        for item in config['aliases']:
            mappings[item['alias']] = item['command']
        return mappings

    intro = "Welcome to the RAN Fusion Simulator CLI.\nType --help to list commands.\n"
    prompt = '\033[1;32m(Cli-host)\033[0m '

    def precmd(self, line):
        line = line.strip()
        if line == 'exit':
            return 'exit'  # Ensures that 'exit' command is recognized and processed
        if line in self.aliases:
            return self.aliases.get(line, line)
        else:
            return line
################################################################################################################################ 
    def do_ue_list(self, arg):
        args = arg.split()
        page = 1
        page_size = 10  # Default number of items per page
        if len(args) == 2:
            try:
                page = int(args[0])
                page_size = int(args[1])
            except ValueError:
                print("Invalid page or page_size. Using defaults.")
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        total_ues = len(UE.get_ues())
        ues = UE.get_ues()[start_index:end_index]
        table = PrettyTable()
        table.field_names = ["UE ID", "Service Type", "Throughput(MB)"]
        table.align = "l"  # Left-align table contents
        table.border = True  # Ensure borders are enabled for clarity
        table.header = True  # Ensure the header is displayed
        table.header_style = "title"  # Capitalize header titles for emphasis

        for ue in ues:
            throughput_mbps = ue.throughput / 1e6  # Convert throughput to Mbps
            table.add_row([ue.ID, ue.ServiceType, f"{throughput_mbps:.2f}"])  # Format throughput for consistency

        print(table)
        total_pages = total_ues // page_size + (1 if total_ues % page_size > 0 else 0)
        print(f"Page {page} of {total_pages}")
############################################################################################################################## 
    def do_ue_log(self, arg):
        """Display UE (User Equipment) traffic logs."""
        print("Displaying UE traffic logs. Press Ctrl+C to return to the CLI.")
        try:
            # Initialize PrettyTable with column headers based on your log structure
            table = PrettyTable(["UE ID", "Service Type", "Throughput (MB)", "Interval (s)", "Delay (ms)", "Jitter (%)", "Packet Loss Rate (%)"])
            with open('traffic_logs.txt', 'r') as log_file:
                for line in log_file:
                    # Assuming each log entry is a comma-separated value line
                    # You'll need to adjust parsing based on your actual log format
                    parts = line.split(',')  # This is an example; adjust based on your actual log format
                    if len(parts) < 7:
                        continue  # Skip malformed lines
                    # Add a row to the table for each log entry
                    # Adjust index and parsing as necessary based on the actual log format
                    table.add_row(parts)
            print(table)
        except FileNotFoundError:
            print("Log file not found. Ensure traffic logging is enabled.")
        except KeyboardInterrupt:
            print("\nReturning to CLI...")
################################################################################################################################ 
    def do_gnb_list(self, arg):
        """List all gNodeBs with details."""
        gNodeB_details_list = self.gNodeB_manager.list_all_gNodeBs_detailed()
        gNodeB_loads = self.network_load_manager.calculate_gNodeB_load()
        if not gNodeB_details_list:
            print("No gNodeBs found.")
            return

        # Create a PrettyTable instance
        table = PrettyTable()

        # Define the table columns
        table.field_names = ["gNodeB ID", "Latitude", "Longitude", "Coverage Radius", "Transmission Power", "Bandwidth", "Load %"]

        # Adding rows to the table
        for gNodeB in gNodeB_details_list:
            # Example of accessing other details assuming they exist in your data structure
            coverage_radius = gNodeB.get('coverage_radius', 'N/A')
            transmission_power = gNodeB.get('transmission_power', 'N/A')
            bandwidth = gNodeB.get('bandwidth', 'N/A')
            load_percentage = gNodeB_loads.get(gNodeB['id'], 0)
            table.add_row([
                gNodeB['id'], 
                gNodeB['latitude'], 
                gNodeB['longitude'], 
                coverage_radius, 
                transmission_power, 
                bandwidth,
                f"{load_percentage:.2f}%" 
            ])
    
        # Optional: Set alignment for each column if needed
        table.align = "l"  # Left align the text
    
        # Print the table
        print(table) 
################################################################################################################################ 
    def do_cell_list(self, arg):
        """List all cells with their load percentage."""
        cell_details_list = self.cell_manager.list_all_cells_detailed()
        if not cell_details_list:
            print("No cells found.")
            return

        table = PrettyTable()
        table.field_names = ["Cell ID", "Technology", "Status", "Active UEs", "Cell Load (%)"]

        for cell_detail in cell_details_list:
            cell_id = cell_detail['id']
            cell = self.cell_manager.get_cell(cell_id)  # Retrieve the cell object by its ID
            if cell is None:
                continue  # Skip if the cell is not found

            technology = cell_detail.get('technology', '5GNR')
            status_text = "\033[92mActive\033[0m" if cell_detail.get('Active', True) else "\033[91mInactive\033[0m"
            active_ues = self.calculate_active_ues_for_cell(cell_id)  # Calculate active UEs for each cell

            # Calculate the load of the cell using the NetworkLoadManager
            cell_load_percentage = self.network_load_manager.calculate_cell_load(cell)
            
            table.add_row([
                cell_id,
                technology,
                status_text,
                active_ues,
                f"{cell_load_percentage:.2f}%"  # Format the cell load as a percentage
            ])

        table.align = "l"
        print(table)

    def calculate_active_ues_for_cell(self, cell_id):
        # Retrieve the cell object by its ID using the correct method name
        cell = self.cell_manager.get_cell(cell_id)
        if cell is None:
            return 0  # Return 0 if the cell is not found
        # Return the count of active UEs for the cell
        return len(cell.ConnectedUEs)
################################################################################################################################ 
    def do_sector_list(self, arg):
        """List all sectors"""
        sector_list = self.sector_manager.list_all_sectors()
        if not sector_list:
            print("No sectors found.")
            return
        # Create a PrettyTable instance
        table = PrettyTable()
        # Define the table columns including Current Load (%)
        table.field_names = ["Sector ID", "Cell ID", "Max UEs", "Active UEs", "Max Throughput", "Current Load (%)"]
        # Adding rows to the table
        for sector_info in sector_list:
            # No need to create a Sector instance, just use the sector_info directly
            table.add_row([
                sector_info['sector_id'],
                sector_info['cell_id'],
                sector_info['capacity'],
                sector_info['current_load'],
                sector_info['max_throughput'],
                f"{sector_info['current_load']:.2f}%"  # Assuming 'current_load' is a percentage
            ])
        # Optional: Set alignment for each column
        table.align["Sector ID"] = "l"
        table.align["Cell ID"] = "l"
        table.align["Max UEs"] = "r"
        table.align["Active UEs"] = "r"
        table.align["Max Throughput"] = "r"
        table.align["Current Load (%)"] = "r"  # Align the new column to the right
        # Print the table
        print(table)

################################################################################################################################            
    def do_del_ue(self, ue_id):
        if not ue_id:
            print("Please provide a UE ID.")
            return
        try:
            # Ensure the UE ID is in the correct format (e.g., "UE10")
            formatted_ue_id = f"UE{ue_id}".upper()  # Adjust based on your UE ID format

            # Use the existing ue_manager instance to delete the UE
            if self.ue_manager.delete_ue(formatted_ue_id):
                print(f"UE {formatted_ue_id} has been successfully removed.")
            else:
                print(f"Error removing UE: UE with ID {formatted_ue_id} not found or could not be removed.")
        except Exception as e:
            print(f"Error removing UE: {e}")
################################################################################################################################
    def handle_command(command):
        # Assuming the command format is "add_ue ue <UE_ID>,<Sector_ID>,<Service_Type>"
            _, ue_id, sector_id, service_type = command.split()
            add_ue(ue_id, sector_id, service_type)

    def add_ue(ue_id, sector_id, service_type):
        # You would call a method here to handle the addition of the UE.
        # This method would need to be defined in a suitable class, such as UeManager.
        # It would involve creating a new UE instance with the specified parameters
        # and adding it to the specified sector.
        ue_config = {
            "ue_id": ue_id,
            "connected_sector": sector_id,
            "service_type": service_type
        }
        # Assuming UEManager is already instantiated and accessible
        ue_manager.create_ue(ue_config)
################################################################################################################################ 
    def do_kpis(self, arg):
        """
        Display KPIs for the network.
        This method is triggered by typing 'kpis' in the CLI.
        """
        # Implement the logic to display KPIs as table.

        print("Displaying network KPIs...")

    def do_loadbalancing(self, arg):
        """
        call loadbalancing manually triggered by typing 'loadbalancing' in the CLI.the optimze the load of the each cell/sector
        """
        # Implement the logic call display load balancing information here.
        print("Displaying load balancing massagage...")

################################################################################################################################ 
    def print_global_help(self):

        print(f"\n{Style.BRIGHT}Global options:{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}--help{Fore.RESET}        Show this help message and exit")
        print(f"\n{Style.BRIGHT}Available commands:{Style.RESET_ALL}")
        for command, description in [
            ('cell_list', 'List all cells in the network.'),
            ('gnb_list', 'List all gNodeBs in the network.'),
            ('sector_list', 'List all sectors in the network.'),
            ('ue_list', 'List all UEs (User Equipments) in the network.'),
            ('ue_log', 'Display UE traffic logs.'),
            ('del_ue', 'delete ue from sector and database'),
            ('add_ue', 'add new ue based on current config file to the spesefic sector',),
            ('kpis', 'Display KPIs for the network.'),
            ('loadbalancing', 'Display load balancing information for the network.'),
            ('start_ue', 'Start the ue traffic.'),
            ('stop_ue', 'Stop the ue traffic.'),
            ('exit', 'Exit the Simulator.')
        ]:
            print(f"  {Fore.CYAN}{command}{Fore.RESET} - {description}")
        print()
################################################################################################################################ 
    def do_stop_ue(self, arg):
        """Stop traffic generation for a specific UE."""
        if not arg:
            print("Please provide a UE ID.")
            return
        try:
            # Ensure the UE ID is in the correct format (e.g., "UE10")
            ue_id = f"UE{arg}"
            # Retrieve the UE object using the UE ID
            ue = UE.get_ue_instance_by_id(ue_id)
            if not ue:
                print(f"UE with ID {ue_id} not found.")
                return
            # Assuming there's a method in ue_manager to stop traffic for a UE
            self.traffic_controller.stop_ue_traffic(ue)
            print(f"Traffic generation for UE {ue.ID} has been stopped.")
        except Exception as e:
            print(f"Error stopping traffic for UE: {e}")

    def do_start_ue(self, arg):
        """Start traffic generation for a specific UE."""
        if not arg:
            print("Please provide a UE ID.")
            return
        try:
            # Ensure the UE ID is in the correct format (e.g., "UE10")
            ue_id = f"UE{arg}"
            # Retrieve the UE object using the UE ID
            ue = UE.get_ue_instance_by_id(ue_id)
            if not ue:
                print(f"UE with ID {ue_id} not found.")
                return
            # Call the start_ue_traffic method with the UE object
            self.traffic_controller.start_ue_traffic(ue)
            print(f"Traffic generation for UE {ue.ID} has been started.")
        except Exception as e:
            print(f"Error starting traffic for UE: {e}")
################################################################################################################################
    def complete(self, text, state):
        if state == 0:
            origline = self._orig_line
            line = origline.lstrip()
            stripped = len(origline) - len(line)
            begidx = self._orig_cursor_pos - stripped
            cmd_text = line.split()[0] if line.split() else ''
            mapped_cmd = self.aliases.get(cmd_text, cmd_text)

            if begidx == 0:
                aliased_commands = [alias for alias in self.aliases if alias.startswith(text)]
                command_names = [cmd[3:] for cmd in self.get_names() if cmd.startswith('do_' + text)]
                self.completion_matches = aliased_commands + command_names
            else:
                try:
                    comp_method = getattr(self, 'complete_' + mapped_cmd)
                    self.completion_matches = comp_method(text, line, begidx, state)
                except AttributeError:
                    self.completion_matches = self.complete_default(text, line, begidx, state)

        try:
            return super().complete(text, state) 
        except IndexError:
            return None

    def complete_default(self, text, line, begidx, endidx):
        # Implement your default auto-completion logic here, if any...
        return []

    def complete_gnb_list(self, text, line, begidx, endidx):
        # Assuming self.gNodeB_manager.gnbs is a list of gNodeB names
        if hasattr(self.gNodeB_manager, 'gnbs'):
            return [gnb for gnb in self.gNodeB_manager.gnbs if gnb.startswith(text)]
        return []

    # For alias 'gnb', just delegate to complete_gnb_list
    def complete_gnb(self, *args):
        return self.complete_gnb_list(*args)
    
    def complete_ue_log(self, text, line, begidx, endidx):
        # Since ue_log might not have specific arguments to complete, return an empty list
        # Or, return common log-related suggestions if applicable
        return []
    
    def complete_ulog(self, *args):
        return self.complete_ue_log(*args)
    
    def default(self, line):
        if line == '--help':
            self.print_global_help()
        else:
            print("*** Unknown syntax:", line)

    def do_exit(self, arg):
        """Exit the Simulator."""
        print("Exiting the simulator...")
        return True  # Returning True breaks out of the cmd loop and exits the application.
    