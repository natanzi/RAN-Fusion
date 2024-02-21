#ue_table_display.py
from prettytable import PrettyTable
from network.ue import UE
import sys

class UETableDisplay:
    @staticmethod
    def display_ue_list():
        with UE.ue_lock:  # Ensure thread-safe access to UE data
            ues = list(UE.ue_instances.values())
            table = PrettyTable()
            table.field_names = ["UE ID", "Service Type", "Throughput (Mbps)"]
            for ue in ues:
                table.add_row([ue.ID, ue.ServiceType, f"{ue.throughput / 1e6:.2f}"])
            print(table, file=sys.stdout)