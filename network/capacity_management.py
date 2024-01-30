#capacity_management.py  inside the network folder
from network.sector import get_global_ue_ids
from network import UE
from network.sector import Sector
from network.gNodeB import gNodeB
from network.cell import Cell

class CapacityCalculator:
    def __init__(self, gnodebs, cells, sectors, num_ues_to_launch, global_ue_ids):
        self.gnodebs = gnodebs
        self.cells = cells
        self.sectors = sectors
        self.num_ues_to_launch = num_ues_to_launch
        self.global_ue_ids = global_ue_ids  # Now passed as a parameter

    @property
    def gnodeb_capacity(self):
        return sum(gnb.MaxUEs for gnb in self.gnodebs)
    
    @property
    def cell_capacity(self):
        return sum(cell.maxConnectUes for cell in self.cells)
    
    @property
    def sector_capacity(self):
        return sum(sector.capacity for sector in self.sectors)

    @property
    def connected_ues(self):
        return len(self.global_ue_ids)

    @property
    def max_capacity(self):
        capacities = [self.gnodeb_capacity, 
                        self.cell_capacity, 
                        self.sector_capacity]                      
        return min(capacities)

    def is_within_capacity(self):
        current = self.connected_ues
        requested = self.num_ues_to_launch  
        return (current + requested) <= self.max_capacity
        
    def log_capacity_stats(self):
        print(f"gNodeB Capacity: {self.gnodeb_capacity}")
        print(f"Cell Capacity: {self.cell_capacity}") 
        print(f"Sector Capacity: {self.sector_capacity}")
        print(f"Connected UEs: {self.connected_ues}")
        print(f"Total Capacity: {self.max_capacity}")

