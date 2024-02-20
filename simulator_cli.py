#simulator_cli.py is located in root directory to allows you to type commands like ue-list to see the list of current UEs.
import cmd
from network.ue_manager import UEManager
from network.gNodeB_manager import gNodeBManager
from network.cell_manager import CellManager
from network.sector_manager import SectorManager

class SimulatorCLI(cmd.Cmd):

    intro = 'Welcome to the RAN Fusion simulator CLI. Type help or ? to list commands.\n'
    prompt = '(ran-fusion) '

    def __init__(self, gNodeB_manager, cell_manager, sector_manager, ue_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize the manager instances
        self.gNodeB_manager = gNodeB_manager
        self.cell_manager = cell_manager
        self.sector_manager = sector_manager
        self.ue_manager = ue_manager
################################################################################################################################            
    def do_ue_list(self, arg):
        """List all UEs: ue_list"""
        ue_ids = self.ue_manager.list_all_ues()
        for ue_id in ue_ids:
            ue = self.ue_manager.get_ue_by_id(ue_id)
            print(f"UE ID: {ue.ID}, Service Type: {ue.ServiceType}")
################################################################################################################################
    def do_ue_log(self, arg):
        """Display UE traffic logs: ue_log"""
        try:
            with open('traffic_logs.txt', 'r') as log_file:
                logs = log_file.readlines()
                for log in logs:
                    print(log.strip())
        except FileNotFoundError:
            print("Log file not found. Ensure traffic logging is enabled and logs are being written to 'traffic_logs.txt'.")
################################################################################################################################            
    def do_gnb_list(self, arg):
        """List all gNodeBs"""
        gNodeB_ids = self.gNodeB_manager.list_all_gNodeBs()
        for id in gNodeB_ids:
            print(id)
################################################################################################################################            
    def do_cell_list(self, arg):
        """List all cells"""
        cell_details_list = self.cell_manager.list_all_cells()
        for cell_details in cell_details_list:
            print(f"Cell ID: {cell_details['cell_id']}")
################################################################################################################################            
    def do_sector_list(self, arg):
        """List all sectors"""
        sector_ids = self.sector_manager.list_all_sectors()
        for id in sector_ids:
            print(id)
################################################################################################################################            
    def do_help(self, arg):
        """Display information about available commands or detailed help for a specific command: help [command]"""
        if arg:
            try:
                doc = getattr(self, 'do_' + arg).__doc__
                if doc:
                    print(f"{arg}:\n    {doc}\n")
                else:
                    print(f"No help available for {arg}")
            except AttributeError:
                print(f"No such command: {arg}")
        else:
            commands = [cmd[3:] for cmd in dir(self) if cmd.startswith('do_')]
            print("Available commands:")
            for command in commands:
                # Improved formatting for command listing
                doc = getattr(self, 'do_' + command).__doc__.split(':')[0]  # Get the first line of the docstring for a brief description
                print(f"  {command} - {doc}")
################################################################################################################################            
    def do_exit(self, arg):
        """Exit the CLI: exit"""
        print("Exiting the CLI.")
        return True  # This stops the CLI loop and exits the CLI