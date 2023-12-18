# The NetworkState class maintains the last state of a network in memory, allowing for updates and
# retrieval of information about gNodeBs, cells, and UEs.
#network_state.py is located in network 
from database.database_manager import DatabaseManager
from datetime import datetime
from influxdb_client import Point, WritePrecision
from logs.logger_config import database_logger
from database.time_utils import get_current_time_ntp, server_pools
time = current_time = get_current_time_ntp()

class NetworkState:
    
    def __init__(self):
        self.gNodeBs = {}
        self.cells = {}
        self.ues = {}
        self.last_update = datetime.min 
        self.db_manager = DatabaseManager(self)
        self.db_manager.set_network_state(self)

    def get_cell_load(self, cell):
        # Assuming there's a method in gNodeB to calculate cell load
        gNodeB = self.gNodeBs.get(cell.gNodeB_ID)
        if gNodeB:
            return gNodeB.calculate_cell_load(cell)
        return None
    
    def update_state(self, gNodeBs, cells, ues):
        # Update gNodeBs and cells normally
        self.gNodeBs = gNodeBs
        self.cells = {cell.ID: cell for cell in cells}

        # Update UEs, but check for duplicates first
        new_ues = {}
        for ue in ues:
            if ue.ID in self.ues:
                raise ValueError(f"Duplicate UE ID {ue.ID} found during state update.")
            new_ues[ue.ID] = ue
        self.ues = new_ues

        # Assign neighbors to cells and update the last update timestamp
        self.assign_neighbors_to_cells()
        self.last_update = get_current_time_ntp()

    
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
########################################################################################################
    def serialize_for_influxdb(self):
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
            database_logger.info("Successfully saved state to InfluxDB")  # Log successful save
        except Exception as e:
            database_logger.error(f"Failed to save state to InfluxDB: {e}")  # Log any exceptions
        finally:
            self.db_manager.close_connection()
        end_time = get_current_time_ntp()

    # Assuming you want to log the start and end times
        database_logger.info(f"Start Time for saving state to InfluxDB: {start_time}")
        database_logger.info(f"End Time for saving state to InfluxDB: {end_time}")
########################################################################################################    
    def print_state(self):
        print("Network State:")
        print("Last Update:", self.last_update)

        print("\ngNodeBs:")
        for gNodeB_id, gNodeB in self.gNodeBs.items():
            print(f"ID: {gNodeB_id}")

        print("\nCells:")
        for cell_id, cell in self.cells.items():
            gNodeB = self.gNodeBs.get(cell.gNodeB_ID)
            neighbors = ', '.join(cell.Neighbors) if hasattr(cell, 'Neighbors') and cell.Neighbors else 'None'
            print(f"ID: {cell_id}, gNodeB: {cell.gNodeB_ID}, Neighbors: {neighbors}")

        print("\nUEs:")
        for ue_id, ue in self.ues.items():
            cell = self.cells.get(ue.ConnectedCellID)
            gNodeB_id = cell.gNodeB_ID if cell else 'Unknown'
            print(f"ID: {ue_id}, Cell: {ue.ConnectedCellID}, gNodeB: {gNodeB_id}")
#############################################################################################################
# Add this method to the NetworkState class
def update_and_save(self, gNodeBs, cells, ues):
    self.update_state(gNodeBs, cells, ues)
    self.save_state_to_influxdb()