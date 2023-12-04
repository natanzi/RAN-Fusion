#to insure that network state class is working
#test_network_state.py located in test folder
# test_network_state.py located in test folder
from network.network_state import NetworkState
# Initialize the network state
network_state = NetworkState()

# Assuming gNodeBs, cells, and ues have been initialized and populated elsewhere in your code
# You would update the network state with these dictionaries
# network_state.update_state(gNodeBs, cells, ues)

# Now, you can get the UE information for UE with ID 'UE10'
ue_info = network_state.get_ue_info('UE10')

if ue_info:
    print(f"UE ID: {ue_info['UE_ID']}")
    print(f"Cell ID: {ue_info['Cell_ID']}")
    print(f"gNodeB ID: {ue_info['gNodeB_ID']}")
    print(f"Neighbor Cells: {ue_info['Neighbors']}")
else:
    print("UE with ID 'UE10' not found.")
