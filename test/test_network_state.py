#to insure that network state class is working
#test_network_state.py located in test folder
# test_network_state.py located in test folder
from network.network_state import NetworkState
# Initialize the network state
network_state = NetworkState()

# Prompt the user to enter the UE ID
ue_id_input = input("Please enter the UE ID like 10: ")

# Now, you can get the UE information for the entered UE ID
ue_info = network_state.get_ue_info(ue_id_input)

if ue_info:
    print(f"UE ID: {ue_info['UE_ID']}")
    print(f"Cell ID: {ue_info['Cell_ID']}")
    print(f"gNodeB ID: {ue_info['gNodeB_ID']}")
    print(f"Neighbor Cells: {ue_info['Neighbors']}")
else:
    print(f"UE with ID '{ue_id_input}' not found.")
