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

class SimulatorCLI(cmd.Cmd):
    def __init__(self, gNodeB_manager, cell_manager, sector_manager, ue_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aliases = {
            'gnb': 'gnb_list',
            'cell': 'cell_list',
            'sector': 'sector_list',
            'ue': 'ue_list',
            'ulog': 'ue_log',  # Alias for ue_log
            'exit': 'quit',
            'help': 'help',
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
            ('ue_log', 'Display UE traffic logs.'),
            ('exit', 'Exit the Simulator.')
        ]:
            print(f"  {cyan}{command}{reset} - {description}")
        print()
################################################################################################################################            
    def do_ue_list(self, arg):
        """List all UEs: ue_list"""
        ue_ids = self.ue_manager.list_all_ues()
        if not ue_ids:
            print("No UEs found.")
            return
        for ue_id in ue_ids:
            ue = self.ue_manager.ues[ue_id]  # Access the UE object directly from the dictionary
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
        gNodeB_details_list = self.gNodeB_manager.list_all_gNodeBs_detailed()
        if not gNodeB_details_list:
            print("No gNodeBs found.")
            return
        for gNodeB in gNodeB_details_list:
            print(f"gNodeB ID: {gNodeB['id']}, Latitude: {gNodeB['latitude']}, Longitude: {gNodeB['longitude']}, etc...")
################################################################################################################################            
    def do_cell_list(self, arg):
        """List all cells"""
        cell_details_list = self.cell_manager.list_all_cells_detailed()
        if not cell_details_list:
            print("No cells found.")
            return
        for cell in cell_details_list:
            print(f"Cell ID: {cell['id']}, etc...")
################################################################################################################################            
    def do_sector_list(self, arg):
        """List all sectors"""
        sector_list = self.sector_manager.list_all_sectors()

        if not sector_list:
            print("No sectors found.")
            return

        # Create a PrettyTable instance
        table = PrettyTable()

        # Define the table columns
        table.field_names = ["Sector ID", "Cell ID", "Max UEs", "Active UEs", "Max Throughput"]

        # Adding rows to the table
        for sector in sector_list:
            table.add_row([sector['sector_id'], sector['cell_id'], sector['capacity'], sector['current_load'], sector['max_throughput']])

        # Optional: Set alignment for each column
        table.align["Sector ID"] = "l"
        table.align["Cell ID"] = "l"
        table.align["Max UEs"] = "r"
        table.align["Active UEs"] = "r"
        table.align["Max Throughput"] = "r"

        # Print the table
        print(table)

################################################################################################################################            
    def do_exit(self, arg):
        """Exit the CLI: exit"""
        print("Exiting the CLI.")
        return True  # This stops the CLI loop and exits the CLI
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
            return self.completion_matches[state]
        except IndexError:
            return None

    def complete_default(self, text, line, begidx, endidx):
        # Implement your default auto-completion logic here, if any...
        return []

    # Example complete_ method for gnb_list (and its alias 'gnb')
    def complete_gnb_list(self, text, line, begidx, endidx):
        # Implement specific auto-completion logic for gnb_list command...
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
################################################################################################################################ 
    def default(self, line):
        if line == '--help':
            self.print_global_help()
        else:
            print("*** Unknown syntax:", line)
    