# The NetworkState class maintains the last state of a network in memory, allowing for updates and
# retrieval of information about gNodeBs, cells, and UEs.
#This class is for Maintain a Network State in Memory
#network_state.py is located in network import datetime
from database.database_manager import DatabaseManager
from datetime import datetime

class NetworkState:
    def __init__(self):
        self.gNodeBs = {}
        self.cells = {}
        self.ues = {}
        self.last_update = datetime.datetime.min
    
    def get_cell_load(self, cell):
        # Assuming there's a method in gNodeB to calculate cell load
        gNodeB = self.gNodeBs.get(cell.gNodeB_ID)
        if gNodeB:
            return gNodeB.calculate_cell_load(cell)
        return None
    
    def update_state(self, gNodeBs, cells, ues):
        self.gNodeBs = gNodeBs
        self.cells = {cell.ID: cell for cell in cells}
        self.ues = {ue.ID: ue for ue in ues}  # Convert list of UEs to a dictionary
        self.assign_neighbors_to_cells()
        self.last_update = datetime.datetime.now()
    
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
    
    def serialize_for_influxdb(self):
        points = []
        for cell_id, cell in self.cells.items():
            cell_load = self.get_cell_load(cell)
            point = {
                "measurement": "cell_load_info",
                "tags": {
                    "Cell_ID": cell_id,
                    "gNodeB_ID": cell.gNodeB_ID,
                    "Neighbors": ','.join(cell.Neighbors) if hasattr(cell, 'Neighbors') else 'None'
                },
                "fields": {
                    "Load": cell_load,
                    # Add other relevant fields here
                },
                "time": datetime.utcnow().isoformat()
            }
            points.append(point)
        return points
    
    def save_state_to_influxdb(self):
        db_manager = DatabaseManager()
        points = self.serialize_for_influxdb()
        for point in points:
            db_manager.write_data(point)
        db_manager.close_connection()
    
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
#network_state = NetworkState()

# Update the network state after initialization or any changes
#network_state.update_state(gNodeBs, cells, ues)

# To get the UE information including its cell and gNodeB
#ue_info = network_state.get_ue_info('UE40')

# To get the cell information including its gNodeB and allocated cells
#cell_info = network_state.get_cell_info('AX340T')

# To get the last update of a specific gNodeB and its allocated cells
#gNodeB_info = network_state.get_gNodeB_last_update('T240')