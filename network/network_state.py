# The NetworkState class maintains the last state of a network in memory, allowing for updates and
# retrieval of information about gNodeBs, cells, and UEs.
#network_state.py is located in network 
from database.database_manager import DatabaseManager
from datetime import datetime
from influxdb_client import Point, WritePrecision
from logs.logger_config import database_logger
from database.time_utils import get_current_time_ntp, server_pools
from logs.logger_config import cell_logger, ue_logger, gnodeb_logger, sector_logger
from multiprocessing import Lock

time = current_time = get_current_time_ntp()

class NetworkState:
    print("Debug: Initializing NetworkState and enter to class.")
    def __init__(self, lock):
        self.lock = lock
        self.gNodeBs = {}
        self.cells = {}
        self.ues = {}
        self.last_update = datetime.min
        self.db_manager = DatabaseManager(self)
        self.db_manager.set_network_state(self)
        self.sectors = {}  # Store sectors by sector_id
        print("Debug: NetworkState initialized.")
        print("Debug: NetworkState instance variables set: ", vars(self))
        print("Debug: Exiting NetworkState __init__ method.")
#################################################################################
    # Clear other relevant state information as needed
    def clear_state(self):
        print("Debug: Clearing network state.")
        self.gNodeBs = {}
        self.cells = {}
        self.UEs = {}
        self.sectors = {}
        print("Debug: Network state cleared.")
#################################################################################
    def has_cell(self, cell_id):
        print(f"Debug: Checking if cell {cell_id} exists in the network state.")
        exists = cell_id in self.cells
        print(f"Debug: Cell {cell_id} {'exists' if exists else 'does not exist'} in the network state.")
        return exists
#################################################################################    
    def update_state(self, gNodeBs, cells, ues):
        print("Debug: Starting state update.")
        with self.lock:
            self.check_for_duplicate_gNodeBs(gNodeBs)
            self.check_for_duplicate_cells(cells)
            self.check_for_duplicate_ues(ues)
            self.check_for_duplicate_sectors()
            self.gNodeBs = gNodeBs
            self.cells = cells
            self.ues = ues
            self.assign_neighbors_to_cells()
            self.last_update = get_current_time_ntp()
        # Call verify_no_duplicates to ensure no duplicates exist after the update
        self.verify_no_duplicates()
        print("Debug: State update completed.")
######################################################################################################
    def check_for_duplicate_gNodeBs(self, gNodeBs):
        print("Debug: Checking for duplicate gNodeBs.")
        seen_gNodeB_ids = set()
        for gNodeB_id in gNodeBs:
            if gNodeB_id in seen_gNodeB_ids:
                gnodeb_logger.error(f"Duplicate gNodeB ID {gNodeB_id} detected during state update.")
                raise ValueError(f"Duplicate gNodeB ID {gNodeB_id} found during state update.")
            seen_gNodeB_ids.add(gNodeB_id)
        print("Debug: Duplicate gNodeB check completed.")
######################################################################################################
    def check_for_duplicate_cells(self, cells):
        print("Debug: Checking for duplicate cells.")
        seen_cell_ids = set()
        for cell_id, cell in cells.items():
            if cell_id in seen_cell_ids:
                cell_logger.error(f"Duplicate cell ID {cell_id} detected during state update.")
                raise ValueError(f"Duplicate cell ID {cell_id} found during state update.")
            seen_cell_ids.add(cell_id)
        print("Debug: Duplicate cell check completed.")
######################################################################################################
    def check_for_duplicate_ues(self, ues):
        print("Debug: Checking for duplicate UEs.")
        seen_ue_ids = set()
        for ue in ues:
            if ue.ID in seen_ue_ids:
                ue_logger.error(f"Duplicate UE ID {ue.ID} detected during state update.")
                raise ValueError(f"Duplicate UE ID {ue.ID} found during state update.")
            seen_ue_ids.add(ue.ID)
        print("Debug: Duplicate UE check completed.")

######################################################################################################
    def check_for_duplicate_sectors(self):
        print("Debug: Checking for duplicate sectors.")
        seen_sector_ids = set()
        for sector_id, sector in self.sectors.items():
            if sector_id in seen_sector_ids:
                sector_logger.error(f"Duplicate sector ID {sector_id} detected during state update.")
                raise ValueError(f"Duplicate sector ID {sector_id} found during state update.")
            seen_sector_ids.add(sector_id)
        print("Debug: Duplicate sector check completed.")
######################################################################################################
    def add_cell(self, cell):
        print(f"Debug: Adding cell {cell.ID} to network state.")
        with self.lock:  # Ensure thread safety
            if cell.ID in self.cells:
                error_message = f"Duplicate cell ID {cell.ID} detected. Skipping addition."
                cell_logger.error(error_message)
                print(f"Debug: {error_message}")
                raise ValueError(error_message)
            else:
                self.cells[cell.ID] = cell
                cell_logger.info(f"Cell {cell.ID} added to the network state.")
                print(f"Debug: Cell {cell.ID} added to the network state.")
        print(f"Debug: Cell {cell.ID} addition completed.")
######################################################################################################
    def verify_no_duplicates(self):
        with self.lock:  # Ensure thread safety
            print("Debug: Checking for duplicate cells.")
            if len(self.cells) != len(set(self.cells.keys())):
                print("Error: Duplicate cells detected.")
                raise ValueError("Duplicate cells detected.")
        
            print("Debug: Checking for duplicate UEs.")
            if len(self.ues) != len(set(self.ues.keys())):
                print("Error: Duplicate UEs detected.")
                raise ValueError("Duplicate UEs detected.")
        
            print("Debug: No duplicates found.")    
######################################################################################################
    def find_cell_by_id(self, cell_id):
        print(f"Debug: Finding cell by ID {cell_id}.")
        try:
            # Attempt to retrieve the cell by ID
            cell = self.cells.get(cell_id, None)
            if cell is None:
                # Log if the cell was not found
                cell_logger.warning(f"Cell with ID {cell_id} not found in the network state.")
            print(f"Debug: Cell {cell_id} {'found' if cell else 'not found'} in the network state.")
            return cell
        except Exception as e:
            # Log any exception that occurs during the retrieval
            cell_logger.error(f"An error occurred while finding cell with ID {cell_id}: {e}")
            print(f"Debug: An error occurred while finding cell with ID {cell_id}.")
        return None
######################################################################################################    
    def get_cell_load_for_ue(self, ue_id):
        print(f"Debug: Getting cell load for UE {ue_id}.")
        ue = self.ues.get(ue_id)
        if ue:
            cell_id = ue.ConnectedCellID
            cell = self.cells.get(cell_id)
            if cell:
                # Use the existing calculate_cell_load method from the gNodeB class
                load = self.gNodeBs[cell.gNodeB_id].calculate_cell_load(cell, self.traffic_controller)
                print(f"Debug: Cell load for UE {ue_id} retrieved.")
                return load
        print(f"Debug: Cell load for UE {ue_id} not found.")
        return None  # or an appropriate default value if the UE is not found
######################################################################################################    
    def assign_neighbors_to_cells(self):
        print("Debug: Starting to assign neighbors to cells.")
        for gNodeB_id, gNodeB in self.gNodeBs.items():
            cell_ids = [cell.ID for cell in gNodeB.Cells]
            for cell in gNodeB.Cells:
                cell.Neighbors = [neighbor_id for neighbor_id in cell_ids if neighbor_id != cell.ID]
                print(f"Debug: Neighbors assigned to cell {cell.ID}: {cell.Neighbors}")
######################################################################################################   
    def get_ue_info(self, ue_id):
        print(f"Debug: Retrieving UE info for UE_ID {ue_id}.")
        ue = self.ues.get(ue_id)
        if ue:
            cell_id = ue.ConnectedCellID
            cell = self.cells.get(cell_id)
            if cell:
                gNodeB_id = cell.gNodeB_ID
                neighbors = cell.Neighbors
                print(f"Debug: UE info for UE_ID {ue_id} found.")
                return {
                    'UE_ID': ue_id,
                    'Cell_ID': cell_id,
                    'gNodeB_ID': gNodeB_id,
                    'Neighbors': neighbors
                }
        print(f"Debug: UE info for UE_ID {ue_id} not found.")
        return None
######################################################################################################    
    def get_neighbors_load(self, cell_id):
        print("Debug: Starting get_neighbors_load function.")
        neighbors_load = {}
        cell = self.cells.get(cell_id)
        if cell and hasattr(cell, 'Neighbors'):
            for neighbor_id in cell.Neighbors:
                neighbor_cell = self.cells.get(neighbor_id)
                if neighbor_cell:
                    neighbors_load[neighbor_id] = self.calculate_cell_load(neighbor_cell)
        print("Debug: Finished get_neighbors_load function.")
        return neighbors_load
######################################################################################################
    def get_cell_info(self, cell_id):
        print("Debug: Starting get_cell_info function.")
        cell = self.cells.get(cell_id)
        if cell:
            gNodeB_id = cell.gNodeB_ID
            gNodeB = self.gNodeBs.get(gNodeB_id)
            if gNodeB:
                allocated_cells = [cell.ID for cell in gNodeB.Cells]
                print("Debug: Finished get_cell_info function with result.")
                return {
                    'gNodeB_ID': gNodeB_id,
                    'Allocated_Cells': allocated_cells
                }
        print("Debug: Finished get_cell_info function with no result.")
        return None
######################################################################################################
    def get_gNodeB_last_update(self, gNodeB_id):
        print("Debug: Starting get_gNodeB_last_update function.")
        gNodeB = self.gNodeBs.get(gNodeB_id)
        if gNodeB:
            allocated_cells = [cell.ID for cell in gNodeB.Cells]
            print("Debug: Finished get_gNodeB_last_update function with result.")
            return {
                'Last_Update': gNodeB.last_update,
                'Allocated_Cells': allocated_cells
            }
        print("Debug: Finished get_gNodeB_last_update function with no result.")
        return None
######################################################################################################
    def add_ue(self, ue):
        with self.lock:  # Ensure thread safety
            print("Debug: Starting add_ue function.")
            if ue.ID not in self.ues:
                self.ues[ue.ID] = ue
                ue_logger.info(f"UE {ue.ID} added to the network state.")
                print(f"Debug: UE with ID {ue.ID} added to the network state.")
            else:
                error_message = f"Failed to add UE '{ue.ID}': UE with ID '{ue.ID}' already exists in the network."
                ue_logger.error(error_message)
                print(f"Debug: {error_message}")
            print("Debug: Finished add_ue function.")
######################################################################################################
    def remove_ue(self, ue_id):
        print("Debug: Starting remove_ue function.")
        with self.lock:
            if ue_id in self.ues:
                del self.ues[ue_id]
                print(f"Debug: UE with ID {ue_id} removed from the network state.")
                return True
            else:
                print(f"Debug: UE with ID {ue_id} not found for removal.")
        print("Debug: Finished remove_ue function with no UE removed.")
        return False
######################################################################################################
    def update_ue(self, ue_id, updated_data):
        print("Debug: Starting update_ue function.")
        with self.lock:
            if ue_id not in self.ues:
                print("Debug: Finished update_ue function with UE not existing.")
                return False  # UE does not exist
            # Assuming `updated_data` is a dictionary with the attributes to be updated
            for key, value in updated_data.items():
                setattr(self.ues[ue_id], key, value)
            print("Debug: Finished update_ue function with UE updated.")
            return True
######################################################################################################
    def get_ue(self, ue_id):
        print("Debug: Starting get_ue function.")
        with self.lock:
            ue = self.ues.get(ue_id, None)
            print(f"Debug: Finished get_ue function with {'UE found' if ue else 'no UE found'}.")
            return ue
########################################################################################################
    def add_sector(self, sector):
        print("Debug: Starting add_sector function.")
        with self.lock:
            if sector.sector_id in self.sectors:
                raise ValueError(f"Duplicate sector ID {sector.sector_id} found.")
            if sector.cell_id not in self.cells:
                raise ValueError(f"Cell ID {sector.cell_id} not found.")
            self.sectors[sector.sector_id] = sector
            self.cells[sector.cell_id].add_sector(sector)
            print(f"Debug: Sector {sector.sector_id} added to cell {sector.cell_id}.")
        print("Debug: Finished add_sector function.")
######################################################################################################
    def remove_sector(self, sector_id):
        print("Debug: Starting remove_sector function.")
        with self.lock:
            sector = self.sectors.pop(sector_id, None)
            if sector:
                self.cells[sector.cell_id].remove_sector(sector_id)
                print(f"Debug: Sector {sector_id} removed from cell {sector.cell_id}.")
            else:
                print(f"Debug: Sector {sector_id} not found for removal.")
        print("Debug: Finished remove_sector function.")
######################################################################################################
    def get_sector_info(self, sector_id):
        print("Debug: Starting get_sector_info function.")
        with self.lock:
            sector = self.sectors.get(sector_id)
            if sector:
                cell = self.cells.get(sector.cell_id)
                gNodeB = self.gNodeBs.get(cell.gNodeB_ID) if cell else None
                print("Debug: Finished get_sector_info function with result.")
                return {
                    'Sector_ID': sector_id,
                    'Cell_ID': sector.cell_id,
                    'gNodeB_ID': cell.gNodeB_ID if cell else None,
                    'gNodeB_Info': gNodeB.to_dict() if gNodeB else None
                }
        print("Debug: Finished get_sector_info function with no result.")
        return None
########################################################################################################
    def serialize_for_influxdb(self):
        print("Debug: Serializing network state for InfluxDB started")
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
                print(f"Debug: Serialized point for cell {cell_id}: {cell_point.to_line_protocol()}")
######################################################################################################
    # Serialize gNodeB metrics
        for gNodeB_id, gNodeB in self.gNodeBs.items():
            gNodeB_point = Point("gnodeb_metrics") \
                .tag("gNodeB_ID", gNodeB_id) \
                .field("max_ues", gNodeB.MaxUEs) \
                .field("cell_count", gNodeB.CellCount) \
                .field("last_update", gNodeB.last_update.strftime('%Y-%m-%d %H:%M:%S')) \
                .time(get_current_time_ntp(), WritePrecision.NS) 
            points.append(gNodeB_point)
######################################################################################################
    # Serialize UE metrics
        for ue_id, ue in self.ues.items():
            ue_point = Point("ue_metrics") \
                .tag("UE_ID", ue_id) \
                .field("connected_cell", ue.ConnectedCellID) \
                .time(get_current_time_ntp(), WritePrecision.NS)
            points.append(ue_point)
        print("Debug: Serializing network state for InfluxDB Finished.")
        return points

########################################################################################################
    def save_state_to_influxdb(self):
        print("Debug: Saving network state to InfluxDB started...")
        start_time = get_current_time_ntp()
        points = self.serialize_for_influxdb()
        print(f"Debug: Number of points to save: {len(points)}")
        try:
            self.db_manager.insert_data_batch(points)
            database_logger.info("Successfully saved state to InfluxDB")  # Log successful save
        except Exception as e:
            database_logger.error(f"Failed to save state to InfluxDB: {e}")  # Log any exceptions
        finally:
            self.db_manager.close_connection()
        end_time = get_current_time_ntp()
        print(f"Debug: Saving {len(points)} points to InfluxDB.")
        print(f"Debug: Time taken to save state: {end_time - start_time} seconds.")
        print("Debug: Saving network state to InfluxDB Finished...")
########################################################################################################    
    def print_state(self):
        print("Network State start:")
        print("Debug: Printing network state...")
        print("Last Update:", self.last_update)
        print("\ngNodeBs:")
        for gNodeB_id, gNodeB in self.gNodeBs.items():
            print(f"ID: {gNodeB_id}")
        print("\nCells:")
        for cell_id, cell in self.cells.items():  # self.cells should be a dictionary
            neighbors = ', '.join(cell.Neighbors) if hasattr(cell, 'Neighbors') and cell.Neighbors else 'None'
            print(f"ID: {cell_id}, gNodeB: {cell.gNodeB_ID}, Neighbors: {neighbors}")
        print("\nUEs:")
        # Check if self.ues is a list and handle accordingly
        if isinstance(self.ues, list):
            for ue in self.ues:  # self.ues is a list
                print(f"ID: {ue.ID}, Cell: {ue.ConnectedCellID}, gNodeB: {ue.gNodeB_ID}")
        else:
            for ue_id, ue in self.ues.items():  # self.ues is a dictionary
                print(f"ID: {ue_id}, Cell: {ue.ConnectedCellID}, gNodeB: {ue.gNodeB_ID}")
        print("Network State printing finished!")
#############################################################################################################
# Add this method to the NetworkState class
    def update_and_save(self, gNodeBs, cells, ues):
        print("Debug: Updating and saving network state started...")
        self.update_state(gNodeBs, cells, ues)
        self.save_state_to_influxdb()
        print("Debug: Updating and saving network state finished")
