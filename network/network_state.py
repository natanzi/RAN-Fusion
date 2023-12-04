#network_state.py is located in network
# This class is for Maintain a Network State in Memory
class NetworkState:
    def __init__(self):
        self.gNodeBs = []
        self.cells = {}
        self.ues = {}

    def update_state(self, gNodeBs, cells, ues):
        self.gNodeBs = gNodeBs
        self.cells = {cell.ID: cell for gNodeB in gNodeBs for cell in gNodeB.Cells}
        self.ues = {ue.ID: ue for ue in ues}

    def get_cell_by_gNodeB(self, gNodeB_id):
        return [cell for cell in self.cells.values() if cell.gNodeBID == gNodeB_id]

    def get_ue_by_cell(self, cell_id):
        return [ue for ue in self.ues.values() if ue.ConnectedCellID == cell_id]

# Initialize the network state
network_state = NetworkState()

# Update the network state after initialization or any changes
network_state.update_state(gNodeBs, cells, ues)

# Use the network state for queries
cell_of_gNodeB = network_state.get_cell_by_gNodeB(gNodeB_id)
ues_of_cell = network_state.get_ue_by_cell(cell_id)