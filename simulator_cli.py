#simulator_cli.py is located in root directory to allows you to type commands like ue-list to see the list of current UEs.
import cmd
from network.ue_manager import UEManager  

class SimulatorCLI(cmd.Cmd):
    intro = 'Welcome to the RAN Fusion simulator CLI. Type help or ? to list commands.\n'
    prompt = '(ran-fusion) '

    def __init__(self, ue_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ue_manager = ue_manager

    def do_ue_list(self, arg):
        """List all UEs: ue_list"""
        """This command lists all the User Equipments (UEs) currently managed by the simulator."""

        ue_ids = self.ue_manager.list_all_ues()
        for ue_id in ue_ids:
            ue = self.ue_manager.get_ue_by_id(ue_id)
            print(f"UE ID: {ue.ID}, Service Type: {ue.ServiceType}")
    
    def do_help(self, arg):
        if arg:
            # Show help for a specific command
            try:
                doc = getattr(self, 'do_' + arg).__doc__
                if doc:
                    print(f"{arg}:\n    {doc}\n")
                else:
                    print(f"No help available for {arg}")
            except AttributeError:
                print(f"No such command: {arg}")
        else:
            # List all commands
            commands = [cmd[3:] for cmd in dir(self) if cmd.startswith('do_')]
            print("Available commands:")
            for command in commands:
                print(f"  {command}")

    def do_exit(self, arg):
        'Exit the CLI: exit'
        print("Exiting the CLI.")
        return True  # This stops the CLI loop and exits the CLI