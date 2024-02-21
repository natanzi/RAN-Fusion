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

class SimulatorCLI(cmd.Cmd):
    def __init__(self, gNodeB_manager, cell_manager, sector_manager, ue_manager, *args, **kwargs):
        super().__init__(*args, **kwargs, completekey='tab')
        self.aliases = {
            'gnb': 'gnb_list',
            'cell': 'cell_list',
            'sector': 'sector_list',
            'ue': 'ue_list',
            'ulog': 'ue_log',
            'help': 'help',
            'del': 'delete_ue',
        }
        # This is an efficient way to use the predefined relationships between commands and aliases
        # Map the function executions directly through alias input
        self.gNodeB_manager = gNodeB_manager
        self.cell_manager = cell_manager
        self.sector_manager = sector_manager
        self.ue_manager = ue_manager

    intro = "Welcome to the RAN Fusion Simulator CLI.\nType --help to list commands.\n"
    prompt = '\033[1;32m(Root)\033[0m '

    def precmd(self, line):
        line = line.strip()
        if line in self.aliases:
            return self.aliases.get(line, line)
        else:
            return line
        
    def precmd(self, line):
        line = line.strip()
        if line == 'exit':
            return 'exit'  # Directly return 'exit' to trigger do_exit
        if line in self.aliases:
            return self.aliases[line]
        else:
            return line
################################################################################################################################ 
    def do_ue_list(self, arg):
        """List all UEs: ue_list"""
        ue_ids = self.ue_manager.list_all_ues()
        if not ue_ids:
            print("No UEs found.")
            return
        table = PrettyTable()
        table.field_names = ["UE ID", "Service Type"]
        for ue_id in ue_ids:
            ue = self.ue_manager.get_ue_by_id(ue_id)
            table.add_row([ue.ID, ue.ServiceType])
        print(table)
############################################################################################################################### 
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
        if not gNodeB_details_list:
            print("No gNodeBs found.")
            return
    
        # Create a PrettyTable instance
        table = PrettyTable()
    
        # Define the table columns
        # Assuming 'etc...' includes fields like 'CoverageRadius', 'TransmissionPower', etc.
        # Adjust the field names based on your actual data structure
        table.field_names = ["gNodeB ID", "Latitude", "Longitude", "Coverage Radius", "Transmission Power", "Bandwidth"]
    
        # Adding rows to the table
        for gNodeB in gNodeB_details_list:
            # Example of accessing other details assuming they exist in your data structure
            coverage_radius = gNodeB.get('coverage_radius', 'N/A')
            transmission_power = gNodeB.get('transmission_power', 'N/A')
            bandwidth = gNodeB.get('bandwidth', 'N/A')
        
            table.add_row([
                gNodeB['id'], 
                gNodeB['latitude'], 
                gNodeB['longitude'], 
                coverage_radius, 
                transmission_power, 
                bandwidth
            ])
    
        # Optional: Set alignment for each column if needed
        table.align = "l"  # Left align the text
    
        # Print the table
        print(table) 
################################################################################################################################ 
    def do_cell_list(self, arg):
        """List all cells"""
        cell_details_list = self.cell_manager.list_all_cells_detailed()
        if not cell_details_list:
            print("No cells found.")
            return
    
        # Create a PrettyTable instance
        table = PrettyTable()
    
        # Define the table columns
        # Assuming you want to include more details such as 'Technology', 'Status', etc.
        # Adjust the field names based on your actual data structure and what you wish to display
        table.field_names = ["Cell ID", "Technology", "Status", "Active UEs"]
    
        # Adding rows to the table
        for cell in cell_details_list:
            # Here, I'm using placeholders for additional cell details. Replace these with actual data fields.
            technology = cell.get('technology', 'N/A')  # Example placeholder
            status = cell.get('status', 'N/A')  # Example placeholder
            active_ues = cell.get('active_ues', 'N/A')  # Example placeholder
        
            table.add_row([
                cell['id'], 
                technology, 
                status, 
                active_ues
            ])
    
        # Optional: Set alignment for each column if needed
        table.align = "l"  # Left align the text
    
        # Print the table
        print(table)
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
    #def do_delete_ue(self, arg):
      #  """Delete a UE by its ID: delete_ue <ue_id>"""
      #  if not arg:
      #      print("Please specify the UE ID.")
     #   return
  #  try:
        # Assuming your UEManager has a method `delete_ue` for deleting a UE by its ID
     #   success = self.ue_manager.delete_ue(arg)
     #   if success:
     #       print(f"UE with ID {arg} deleted successfully.")
     #   else:
  #          print(f"Failed to delete UE with ID {arg}.")
  #  except Exception as e:
    #    print(f"Error deleting UE with ID {arg}: {e}")
################################################################################################################################ 
    def print_global_help(self):
        """Prints help for global options."""
        bold = '\033[1m'
        reset = '\033[0m'
        green = '\033[32m'
        cyan = '\033[36m'

        print(f"\n{bold}Global options:{reset}")
        print(f"  {green}--help{reset}\tShow this help message and exit")
        print(f"\n{bold}Available commands:{reset}")
        for command, description in [
            ('cell_list', 'List all cells in the network.'),
            ('gnb_list', 'List all gNodeBs in the network.'),
            ('sector_list', 'List all sectors in the network.'),
            ('ue_list', 'List all UEs (User Equipments) in the network.'),
            ('ue_log', 'Display UE traffic logs.'),
            ('exit', 'Exit the Simulator.')
        ]:
            print(f"  {cyan}{command}{reset} - {description}")
        print()
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
    