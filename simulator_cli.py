#simulator_cli.py is located in root directory to allows you to type commands like ue-list to see the list of current UEs.
import cmd
import time
import textwrap
from functools import partial
from network.ue_manager import UEManager
from network.gNodeB_manager import gNodeBManager
from network.cell_manager import CellManager
from network.sector_manager import SectorManager

class SimulatorCLI(cmd.Cmd):

    def __init__(self, gNodeB_manager, cell_manager, sector_manager, ue_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aliases = {
        'gnb': 'gnb_list',
        }
        # Initialize the manager instances
        self.gNodeB_manager = gNodeB_manager
        self.cell_manager = cell_manager
        self.sector_manager = sector_manager
        self.ue_manager = ue_manager


    intro = textwrap.dedent("""
        Welcome to the RAN Fusion Simulator CLI.
        Type --help  to list commands.
        """) + "\n" + "Type --help for global options.\n"

    prompt = '\033[1;32m(Root)\033[0m '
    
    # ASCII Art Banner for CLI Start
    #print("""
    #______               _   _   ______                 _                      _____   _        _____ 
    #|  __ \      /\     | \ | | |  ____|               (_)                    / ____| | |      |_   _|
    #| |__) |    /  \    |  \| | | |__     _   _   ___   _    ___    _ __     | |      | |        | |  
    #|  _  /    / /\ \   | . ` | |  __|   | | | | / __| | |  / _ \  | '_ \    | |      | |        | |  
    #| | \ \   / ____ \  | |\  | | |      | |_| | \__ \ | | | (_) | | | | |   | |____  | |____   _| |_ 
    #|_|  \_\ /_/    \_\ |_| \_| |_|       \__,_| |___/ |_|  \___/  |_| |_|    \_____| |______| |_____|
    #""")            
    
    def precmd(self, line):
        line = line.strip()
        if line in self.aliases:
            return self.aliases[line]
        else:
            return line

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
            ('ue_log', 'Display UE (User Equipment) traffic logs.'),
            ('exit', 'Exit the Simulator.')
        ]:
            print(f"  {cyan}{command}{reset} - {description}")
        print()
################################################################################################################################            
    def do_ue_list(self, arg):
        """List all UEs: ue_list"""
        ue_ids = self.ue_manager.list_all_ues()
        for ue_id in ue_ids:
            ue = self.ue_manager.get_ue_by_id(ue_id)
            print(f"UE ID: {ue.ID}, Service Type: {ue.ServiceType}")
################################################################################################################################
    def do_ue_log(self, arg):
        """Display UE (User Equipment) traffic logs. Press Ctrl+C to return to the CLI."""
        print("Displaying UE traffic logs. Press Ctrl+C to return to the CLI.")
        try:
            with open('traffic_logs.txt', 'r') as log_file:
                # Go to the end of the file to display only new logs
                log_file.seek(0, 2)
                while True:
                    line = log_file.readline()
                    if not line:
                        time.sleep(1)  # Sleep briefly to avoid busy waiting
                        continue
                    print(line, end='')
        except FileNotFoundError:
            print("Log file not found. Ensure traffic logging is enabled.")
        except KeyboardInterrupt:
            print("\nReturning to CLI...")
        # Optionally, clear the command line here if desired
        # This is just a return to signal the method is ending, and control should go back to the cmd loop.
            return
################################################################################################################################            
    def do_gnb_list(self, arg):
        """List all gNodeBs with details"""
        gNodeB_details_list = self.gNodeB_manager.list_all_gNodeBs()

        if not gNodeB_details_list:
            print("No gNodeBs found.")
            return

        # Define header with additional details
        header = f"{'gNodeB ID':<15} {'Name':<20} {'Location':<20} {'Capacity':<10} {'Current Load':<15}"
        print(header)
        print('-' * len(header))
    
        # Assuming each item in gNodeB_details_list is a dictionary with the required details
        for gNodeB in gNodeB_details_list:
            # Example dictionary keys: 'id', 'name', 'location', 'capacity', 'current_load'
            print(f"{gNodeB.get('id', 'N/A'):<15} {gNodeB.get('name', 'N/A'):<20} {gNodeB.get('location', 'N/A'):<20} {gNodeB.get('capacity', 'N/A'):<10} {gNodeB.get('current_load', 'N/A'):<15}")
################################################################################################################################            
    def do_cell_list(self, arg):
        """List all cells"""
        cell_details_list = self.cell_manager.list_all_cells()

        if not cell_details_list:
            print("No cells found.")
            return

        # Define header with additional details
        header = f"{'Cell ID':<15} {'Cell Name':<20} {'Max UEs':<10} {'Active UEs':<12}"
        print(header)
        print('-' * len(header))
    
        # Print each cell's details in a formatted way
        for cell in cell_details_list:
            print(f"{cell['cell_id']:<15} {cell.get('cell_name', 'N/A'):<20} {cell.get('max_ues', 'N/A'):<10} {cell.get('active_ues', 'N/A'):<12}")
################################################################################################################################            
    def do_sector_list(self, arg):
        """List all sectors"""
        sector_list = self.sector_manager.list_all_sectors()

        if not sector_list:
            print("No sectors found.")
            return

        # Adjusted the spacing in the headers and data rows to match your output
        header = f"{'Sector ID':<12} {'Cell ID':<12} {'Max UEs':<12} {'Active UEs':<17} {'Max Throughput':<15}"
        print(header)
        print('-' * len(header))

        # Adjusting print format for each sector's details to align under headers correctly
        for sector in sector_list:
            print(f"{sector['sector_id']:<12} {sector['cell_id']:<12} {sector['capacity']:<12} {sector['current_load']:<17} {sector['max_throughput']:<15}")

################################################################################################################################            
    def do_exit(self, arg):
        """Exit the CLI: exit"""
        print("Exiting the CLI.")
        return True  # This stops the CLI loop and exits the CLI
################################################################################################################################
    def complete(self, text, state):
        if state == 0:  # on first trigger, build possible matches list
            origline = self._orig_line
            line = origline.lstrip()
            stripped = len(origline) - len(line)
            begidx = self._orig_cursor_pos - stripped
            if begidx > 0:
                self.completion_matches = super().complete(text, state)
            else:
                # This is the start of the line, so check for aliases
                aliased_commands = [self.aliases[alias] for alias in self.aliases if alias.startswith(text)]
                self.completion_matches = aliased_commands

        try:
            return self.completion_matches[state]
        except IndexError:
            return None
################################################################################################################################ 
    def default(self, line):
        if line == '--help':
            self.print_global_help()
        else:
            print("*** Unknown syntax:", line)
    