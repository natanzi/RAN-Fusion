# The NetworkState class maintains the last state of a network in memory, allowing for updates and
# retrieval of information about gNodeBs, cells, and UEs.
#network_state.py is located in network 
from database.database_manager import DatabaseManager
from datetime import datetime
from influxdb_client import Point, WritePrecision
from logs.logger_config import database_logger
from database.time_utils import get_current_time_ntp, server_pools
from logs.logger_config import cell_logger, ue_logger, gnodeb_logger, sector_logger
time = current_time = get_current_time_ntp()

class NetworkState:
    def __init__(self, lock):
        self.lock = lock
        self.gNodeBs = {}
        self.cells = {}
        self.ues = {}
        self.last_update = datetime.min
        self.db_manager = DatabaseManager(self)
        self.db_manager.set_network_state(self)
        self.sectors = {}  # Store sectors by sector_id
    
    # Clear other relevant state information as needed
    def clear_state(self):
        self.gNodeBs = {}
        self.cells = {}
        self.UEs = {}
        self.sectors = {}
        
    def has_cell(self, cell_id):
        return cell_id in self.cells
    
    def update_state(self, gNodeBs, cells, ues):
        with self.lock:  # Ensure thread-safe operations
            # Check for duplicates before updating
            self.check_for_duplicate_gNodeBs(gNodeBs)
            self.check_for_duplicate_cells(cells)
            self.check_for_duplicate_ues(ues)
            self.check_for_duplicate_sectors()

            # Update gNodeBs, cells, and UEs
            self.gNodeBs = gNodeBs
            self.cells = cells
            self.ues = ues

            # Assign neighbors to cells and update the last update timestamp
            self.assign_neighbors_to_cells()
            self.last_update = get_current_time_ntp()

    def check_for_duplicate_cells(self, cells):
        seen_cell_ids = set()
        for cell in cells:
            if cell.ID in seen_cell_ids:
                cell_logger.error(f"Duplicate cell ID {cell.ID} detected during state update.")
                raise ValueError(f"Duplicate cell ID {cell.ID} found during state update.")
            seen_cell_ids.add(cell.ID)

    def check_for_duplicate_gNodeBs(self, gNodeBs):
        seen_gNodeB_ids = set()
        for gNodeB in gNodeBs.values():  # Change here to iterate over values
            if gNodeB.ID in seen_gNodeB_ids:
                gnodeb_logger.error(f"Duplicate gNodeB ID {gNodeB.ID} detected during state update.")
                raise ValueError(f"Duplicate gNodeB ID {gNodeB.ID} found during state update.")
            seen_gNodeB_ids.add(gNodeB.ID)

    def check_for_duplicate_ues(self, ues):
        seen_ue_ids = set()
        for ue in ues:
            if ue.ID in seen_ue_ids:
                ue_logger.error(f"Duplicate UE ID {ue.ID} detected during state update.")
                raise ValueError(f"Duplicate UE ID {ue.ID} found during state update.")
            seen_ue_ids.add(ue.ID)

    def check_for_duplicate_sectors(self):
        seen_sector_ids = set()
        for sector_id, sector in self.sectors.items():
            if sector_id in seen_sector_ids:
                sector_logger.error(f"Duplicate sector ID {sector_id} detected during state update.")
                raise ValueError(f"Duplicate sector ID {sector_id} found during state update.")
            seen_sector_ids.add(sector_id)

    def add_cell(self, cell):
        with self.lock:  # Assuming a threading lock is used for thread-safe operations
            if cell.ID in self.cells:
                cell_logger.error(f"Duplicate cell ID {cell.ID} detected. Skipping addition.")
                raise ValueError(f"Cell {cell.ID} already exists in the network state.")
            else:
                self.cells[cell.ID] = cell
                cell_logger.info(f"Cell {cell.ID} added to the network state.")

    def find_cell_by_id(self, cell_id):
    #"""
    #Finds a cell by its ID within the network state's list of cells.
    
    #:param cell_id: The ID of the cell to find.
    #:return: The cell with the matching ID or None if not found.
    #"""
        try:
            # Attempt to retrieve the cell by ID
            cell = self.cells.get(cell_id, None)
            if cell is None:
                # Log if the cell was not found
                cell_logger.warning(f"Cell with ID {cell_id} not found in the network state.")
            return cell
        except Exception as e:
        # Log any exception that occurs during the retrieval
            cell_logger.error(f"An error occurred while finding cell with ID {cell_id}: {e}")
        return None
    
    def get_cell_load_for_ue(self, ue_id):
    # Find the cell for the given UE
        ue = self.ues.get(ue_id)
        if ue:
            cell_id = ue.ConnectedCellID
            cell = self.cells.get(cell_id)
            if cell:
            # Use the existing calculate_cell_load method from the gNodeB class
                return self.gNodeBs[cell.gNodeB_id].calculate_cell_load(cell, self.traffic_controller)
        return None  # or an appropriate default value if the UE is not found
    
    def assign_neighbors_to_cells(self):
        for gNodeB_id, gNodeB in self.gNodeBs.items():
            cell_ids = [cell.ID for cell in gNodeB.Cells]
            for cell in gNodeB.Cells:
                cell.Neighbors = [neighbor_id for neighbor_id in cell_ids if neighbor_id != cell.ID]
    
    def get_ue_info(self, ue_id):
        ue = self.ues.get(ue_id)
        if ue:
            cell_id = ue.ConnectedCellID
            cell = self.cells.get(cell_id)
            if cell:
                gNodeB_id = cell.gNodeB_ID
                neighbors = cell.Neighbors
                return {
                    'UE_ID': ue_id,
                    'Cell_ID': cell_id,
                    'gNodeB_ID': gNodeB_id,
                    'Neighbors': neighbors
                }
        return None
    
    def get_neighbors_load(self, cell_id):
        neighbors_load = {}
        cell = self.cells.get(cell_id)
        if cell and hasattr(cell, 'Neighbors'):
            for neighbor_id in cell.Neighbors:
                neighbor_cell = self.cells.get(neighbor_id)
                if neighbor_cell:
                    neighbors_load[neighbor_id] = self.calculate_cell_load(neighbor_cell)
        return neighbors_load
    
    def get_cell_info(self, cell_id):
        cell = self.cells.get(cell_id)
        if cell:
            gNodeB_id = cell.gNodeB_ID
            gNodeB = self.gNodeBs.get(gNodeB_id)
            if gNodeB:
                allocated_cells = [cell.ID for cell in gNodeB.Cells]
                return {
                    'gNodeB_ID': gNodeB_id,
                    'Allocated_Cells': allocated_cells
                }
        return None

    def get_gNodeB_last_update(self, gNodeB_id):
        gNodeB = self.gNodeBs.get(gNodeB_id)
        if gNodeB:
            allocated_cells = [cell.ID for cell in gNodeB.Cells]
            return {
                'Last_Update': gNodeB.last_update,
                'Allocated_Cells': allocated_cells
            }
        return None
    
    def add_ue(self, ue):
        if ue.ID not in self.ues:
            self.ues[ue.ID] = ue
            ue_logger.info(f"UE {ue.ID} added to the network state.")
        else:
            ue_logger.error(f"Failed to add UE '{ue.ID}': UE with ID '{ue.ID}' already exists in the network.")

    def remove_ue(self, ue_id):
        with self.lock:
            if ue_id in self.ues:
                del self.ues[ue_id]
                return True
            return False

    def update_ue(self, ue_id, updated_data):
        with self.lock:
            if ue_id not in self.ues:
                return False  # UE does not exist
            # Assuming `updated_data` is a dictionary with the attributes to be updated
            for key, value in updated_data.items():
                setattr(self.ues[ue_id], key, value)
            return True

    def get_ue(self, ue_id):
        with self.lock:
            return self.ues.get(ue_id, None)
########################################################################################################
    def add_sector(self, sector):
        with self.lock:
            if sector.sector_id in self.sectors:
                raise ValueError(f"Duplicate sector ID {sector.sector_id} found.")
            if sector.cell_id not in self.cells:
                raise ValueError(f"Cell ID {sector.cell_id} not found.")
            self.sectors[sector.sector_id] = sector
            self.cells[sector.cell_id].add_sector(sector)

    def remove_sector(self, sector_id):
        with self.lock:
            sector = self.sectors.pop(sector_id, None)
            if sector:
                self.cells[sector.cell_id].remove_sector(sector_id)

    def get_sector_info(self, sector_id):
        with self.lock:
            sector = self.sectors.get(sector_id)
            if sector:
                cell = self.cells.get(sector.cell_id)
                gNodeB = self.gNodeBs.get(cell.gNodeB_ID) if cell else None
                return {
                    'Sector_ID': sector_id,
                    'Cell_ID': sector.cell_id,
                    'gNodeB_ID': cell.gNodeB_ID if cell else None,
                    'gNodeB_Info': gNodeB.to_dict() if gNodeB else None
                }
        return None       
########################################################################################################
    def serialize_for_influxdb(self):
        with self.lock:
            points = []

        # Serialize cell metrics
        for cell_id, cell in self.cells.items():
            cell_load = self.get_cell_load(cell)
            gNodeB = self.gNodeBs.get(cell.gNodeB_ID)
            if gNodeB:
                cell_point = Point("cell_metrics") \
                    .tag("Cell_ID", cell_id) \
                    .tag("gNodeB_ID", cell.gNodeB_ID) \
                    .field("total_cells", len(gNodeB.Cells)) \
                    .field("last_update", gNodeB.last_update.strftime('%Y-%m-%d %H:%M:%S')) \
                    .field("cell_load", cell_load) \
                    .time(get_current_time_ntp(), WritePrecision.NS) 
                points.append(cell_point)
                database_logger.info(f"Serialized data for InfluxDB for Cell ID {cell_id} with load {cell_load}")

    # Serialize gNodeB metrics
        for gNodeB_id, gNodeB in self.gNodeBs.items():
            gNodeB_point = Point("gnodeb_metrics") \
                .tag("gNodeB_ID", gNodeB_id) \
                .field("max_ues", gNodeB.MaxUEs) \
                .field("cell_count", gNodeB.CellCount) \
                .field("last_update", gNodeB.last_update.strftime('%Y-%m-%d %H:%M:%S')) \
                .time(get_current_time_ntp(), WritePrecision.NS) 
            points.append(gNodeB_point)

    # Serialize UE metrics
        for ue_id, ue in self.ues.items():
            ue_point = Point("ue_metrics") \
                .tag("UE_ID", ue_id) \
                .field("connected_cell", ue.ConnectedCellID) \
                .time(get_current_time_ntp(), WritePrecision.NS)
            points.append(ue_point)

        return points
########################################################################################################
    def save_state_to_influxdb(self):
        start_time = get_current_time_ntp()
        points = self.serialize_for_influxdb()
        try:
            self.db_manager.insert_data_batch(points)
            #database_logger.info("Successfully saved state to InfluxDB")  # Log successful save
        except Exception as e:
            database_logger.error(f"Failed to save state to InfluxDB: {e}")  # Log any exceptions
        finally:
            self.db_manager.close_connection()
        end_time = get_current_time_ntp()

########################################################################################################    
    def print_state(self):
        print("Network State:")
        print("Last Update:", self.last_update)
        print("\ngNodeBs:")
        for gNodeB_id, gNodeB in self.gNodeBs.items():
            print(f"ID: {gNodeB_id}")
        print("\nCells:")
        for cell in self.cells:  # self.cells is a list
        # Assuming each cell has an 'ID' and 'gNodeB_ID' attribute
        # and a 'Neighbors' attribute that is a list of neighbor IDs
            neighbors = ', '.join(cell.Neighbors) if hasattr(cell, 'Neighbors') and cell.Neighbors else 'None'
            print(f"ID: {cell.ID}, gNodeB: {cell.gNodeB_ID}, Neighbors: {neighbors}")
        print("\nUEs:")
        for ue_id, ue in self.ues.items():  # self.ues is a dictionary
            print(f"ID: {ue_id}, Cell: {ue.ConnectedCellID}, gNodeB: {ue.gNodeB_ID}")
#############################################################################################################
# Add this method to the NetworkState class
    def update_and_save(self, gNodeBs, cells, ues):
        self.update_state(gNodeBs, cells, ues)
        self.save_state_to_influxdb()
