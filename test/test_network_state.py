#to insure that network state class is working
#test_network_state.py located in test folder
# test_network_state.py located in test folder
import sys
import os

# Add the parent directory to the sys.path to allow imports from the parent directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from network.network_state import NetworkState

# Initialize the network state
network_state = NetworkState()

# Prompt the user to enter the UE ID
ue_id_input = input("Please enter the UE ID liue2ke 'UE2': ")

# Now, you can get the UE information for the entered UE ID
ue_info = network_state.get_ue_info(ue_id_input)  # Pass the user input variable

if ue_info:
    print(f"UE ID: {ue_info['UE_ID']}")
    print(f"Cell ID: {ue_info['Cell_ID']}")
    print(f"gNodeB ID: {ue_info['gNodeB_ID']}")
    print(f"Neighbor Cells: {ue_info['Neighbors']}")
else:
    print(f"UE with ID '{ue_id_input}' not found.")

