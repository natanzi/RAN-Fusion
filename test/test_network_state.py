#to insure that network state class is working
#test_network_state.py located in test folder
from network.network_state import NetworkState  
# To get the UE information including its cell and gNodeB
ue_info = network_state.get_ue_info('UE40')

# To get the cell information including its gNodeB and allocated cells
cell_info = network_state.get_cell_info('AX340T')

# To get the last update of a specific gNodeB and its allocated cells
gNodeB_info = network_state.get_gNodeB_last_update('T240')
