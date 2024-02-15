#NetworkLoadManager.py is located in network folder to address future needs around flexibly incorporating more advanced metrics, analytics and load balancing techniques.
#cell load calulcate
# NetworkLoadManager.py
from network.cell import Cell
from network.sector import Sector
from network.cell_manager import CellManager
from network.sector_manager import SectorManager
from network.gNodeB_manager import gNodeBManager

from logs.logger_config import cell_load_logger,sector_load_logger,gnodbe_load_logger
from database.database_manager import DatabaseManager
from network.network_delay import NetworkDelay
import time
from network.loadbalancer import LoadBalancer

class NetworkLoadManager:

    def __init__(self, cell_manager: CellManager, sector_manager: SectorManager):
        self.cell_manager = cell_manager
        self.sector_manager = sector_manager
        self.db_manager = DatabaseManager()
        self.load_balancer = LoadBalancer()
#####################################################################################################################   
    def calculate_sector_load(self, sector: Sector):
        """Calculate the load of a sector based on the number of connected UEs, their throughput, and its capacity.
        :param sector: An instance of the Sector class.
        :return: The load of the sector as a percentage.
        """
        if sector.capacity == 0:
            return 100  # Indicates the sector is overloaded if capacity is 0

        ue_count_load = (len(sector.connected_ues) / sector.capacity) * 100 if sector.capacity else 0

        # Encapsulate throughput capping logic
        total_capped_throughput = self.calculate_capped_throughput(sector)

        # Check for zero max throughput to default to 0 load
        throughput_load = (total_capped_throughput / sector.max_throughput) * 100 if sector.max_throughput else 0
    
        # Use constant weights for configurable relative importance
        COUNT_WEIGHT = 0.7
        TP_WEIGHT = 0.3
        sector_load = COUNT_WEIGHT * ue_count_load + TP_WEIGHT * throughput_load

        return sector_load

    def calculate_capped_throughput(self, sector: Sector):
        """Calculate the total capped throughput for a sector.
        :param sector: An instance of the Sector class.
        :return: The total capped throughput.
        """
        max_share = sector.max_throughput * 0.1
        capped_ue_throughputs = [min(ue.throughput, max_share) for ue in sector.ues.values()]
        return sum(capped_ue_throughputs)
########################################################################################################################   
    def calculate_cell_load(self, cell: Cell):
        """
        Calculate the load of a cell based on the loads of its sectors.
        :param cell: An instance of the Cell class.
        :return: The load of the cell as a percentage.
        """
        # Check if the cell has sectors
        if not cell.sectors:
            return 0  # Return 0 if there are no sectors to avoid division by zero

        # Calculate the load for each sector and store the loads in a list
        sector_loads = [self.calculate_sector_load(sector) for sector in cell.sectors]

        # Calculate the average load of the cell based on its sectors
        cell_load = sum(sector_loads) / len(sector_loads)

        return cell_load
####################################################################################################################   
    def calculate_gNodeB_load(self):
        """
        Calculate the load of each gNodeB based on the loads of its cells.
        :return: A dictionary with gNodeB IDs as keys and their loads as values.
        """
        gNodeB_loads = {}
        for gNodeB_id, gNodeB in self.cell_manager.gNodeBs.items():
            # Directly iterate over the Cells list since it's not a dictionary
            if not gNodeB.Cells:
                gNodeB_loads[gNodeB_id] = 0
                continue
            cell_loads = [self.calculate_cell_load(cell) for cell in gNodeB.Cells]
            gNodeB_load = sum(cell_loads) / len(cell_loads) if cell_loads else 0
            gNodeB_loads[gNodeB_id] = gNodeB_load

            # Log the load of each gNodeB
            cell_load_logger.info(f"gNodeB {gNodeB_id} Load: {gNodeB_load:.2f}%")

        return gNodeB_loads
####################################################################################################################   
    def calculate_network_load(self):
        """
        Calculate the overall network load based on the loads of all cells.

        :return: The average load of the network as a percentage.
        """
        cells = self.cell_manager.cells.values()
        
        if not cells:
            return 0
        
        cell_loads = [self.calculate_cell_load(cell) for cell in cells]
        network_load = sum(cell_loads) / len(cell_loads)

        return network_load
####################################################################################################################   
    def log_and_write_loads(self):

        # Calculate, log, and write the load of each cell
        for cell_id, cell in self.cell_manager.cells.items():
            cell_load = self.calculate_cell_load(cell)
            cell_load_logger.info(f"Cell {cell_id} Load: {cell_load:.2f}%")
            DatabaseManager().write_cell_load(cell_id, cell_load)

        # Optionally, calculate, log, and write the load of each sector
        for sector_id, sector in self.sector_manager.sectors.items():
            sector_load = self.calculate_sector_load(sector)
            # Assuming sector_load_logger and sector_manager exist
            sector_load_logger.info(f"Sector {sector_id} Load: {sector_load:.2f}%")
            DatabaseManager().write_sector_load(sector_id, sector_load)
####################################################################################################################   
    def network_measurement(self):
        
        network_load = self.calculate_network_load()
        print(f"Network Load: {network_load:.2f}%")
        
        # Calculate network delay
        network_delay_calculator = NetworkDelay()
        network_delay = network_delay_calculator.calculate_delay(network_load)
        print(f"Network Delay: {network_delay} ms")
        
        # Write network measurement (both load and delay) to the database
        self.db_manager.write_network_measurement(network_load, network_delay) 
        
##################################################################################################################     
    def monitoring(self):
        """
        This method always monitors sector load, cell load, and network load
        if the network load, cell load or sector load hit a threshold, the method will call the load balancer!
        """
        while True:
            # Calculate and log gNodeB loads
            gNodeB_loads = self.calculate_gNodeB_load()
            for gNodeB_id, load in gNodeB_loads.items():
                if load > 80:  # Assuming 80% as the congestion threshold for gNodeBs
                    gnodbe_load_logger.warning(f"gNodeB {gNodeB_id} is congested with a load of {load:.2f}%.")
                    self.load_balancer.handle_load_balancing('gNodeB', gNodeB_id)

            # Calculate and log cell loads
            for cell_id, cell in self.cell_manager.cells.items():
                cell_load = self.calculate_cell_load(cell)
                if cell_load > 80:  # Assuming 80% as the congestion threshold for cells
                    cell_load_logger.warning(f"Cell {cell_id} is congested with a load of {cell_load:.2f}%.")
                self.load_balancer.handle_load_balancing('cell', cell_id)

            # Calculate and log sector loads
            for sector_id, sector in self.sector_manager.sectors.items():
                sector_load = self.calculate_sector_load(sector)
                if sector_load > 80:  # Assuming 80% as the congestion threshold for sectors
                    sector_load_logger.warning(f"Sector {sector_id} is congested with a load of {sector_load:.2f}%.")
                    self.load_balancer.handle_load_balancing('sector', sector_id)

            # Calculate and log network load
            network_load = self.calculate_network_load()
            if network_load > 80:  # Assuming 80% as the congestion threshold for the network
                cell_load_logger.warning(f"Network is congested with an average load of {network_load:.2f}%.")

            time.sleep(1)  # Adjust sleep time as needed

################################################Finding Neighbors#########################################################
    def get_sorted_entities_by_load(self, entity_id):
        if entity_id.startswith("sector"):  # Assuming sector IDs have a unique prefix
            return self.get_sorted_neighbor_sectors(entity_id)
        elif entity_id.startswith("cell"):  # Assuming cell IDs have a unique prefix
            return self.get_sorted_neighbor_cells(entity_id)
        elif entity_id.startswith("gNodeB"):  # Assuming gNodeB IDs have a unique prefix
            return self.get_sorted_neighbor_gNodeBs(entity_id)
        else:
            raise ValueError("Unknown entity type")

    def get_sorted_neighbor_sectors(self, sector_id):
        neighbors = self.sector_manager.get_neighbor_sectors(sector_id)
        # Calculate load for each neighbor
        neighbor_loads = [(neighbor_id, self.calculate_sector_load(neighbor)) for neighbor_id, neighbor in neighbors.items()]
        # Sort by load
        sorted_neighbors = sorted(neighbor_loads, key=lambda x: x[1], reverse=True)  # Assuming higher load should be first
        return [neighbor[0] for neighbor in sorted_neighbors]

    def get_sorted_neighbor_cells(self, cell_id):
        neighbors = self.cell_manager.get_neighbor_cells(cell_id)
        neighbor_loads = [(neighbor_id, self.calculate_cell_load(neighbor)) for neighbor_id, neighbor in neighbors.items()]
        sorted_neighbors = sorted(neighbor_loads, key=lambda x: x[1], reverse=True)  # Assuming higher load should be first
        return [neighbor[0] for neighbor in sorted_neighbors]

    def get_sorted_neighbor_gNodeBs(self, gNodeB_id):
        neighbors = self.cell_manager.get_neighbor_gNodeBs(gNodeB_id)
        neighbor_loads = [(neighbor_id, self.calculate_gNodeB_load().get(neighbor_id, 0)) for neighbor_id in neighbors]
        sorted_neighbors = sorted(neighbor_loads, key=lambda x: x[1], reverse=True)  # Assuming higher load should be first
        return [neighbor[0] for neighbor in sorted_neighbors]