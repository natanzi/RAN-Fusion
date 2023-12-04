#to insure that network state class is working
#test_network_state.py located in test folder
# test_network_state.py located in test folder
from network.network_state import NetworkState
from main import load_all_configs, initialize_network
import os
def test_network_state_functionality():
    # Load configurations as done in main.py
    base_dir = os.path.dirname(os.path.abspath(__file__))
    gNodeBs_config, cells_config, ue_config = load_all_configs(base_dir)

    # Initialize network components as done in main.py
    num_ues_to_launch = 10  # Or any other number suitable for testing
    gNodeBs, cells, ues = initialize_network(num_ues_to_launch, gNodeBs_config, cells_config, ue_config)

    # Instantiate the NetworkState class
    network_state = NetworkState()

    # Update the network state with the initialized components
    network_state.update_state(gNodeBs, cells, ues)

    # Test the get_ue_info method for a known UE
    ue_id_to_test = 4  # Assuming UE with ID 4 exists
    ue_info = network_state.get_ue_info(ue_id_to_test)

    # Assert that ue_info is not None and contains expected data
    assert ue_info is not None, "UE information should not be None"
    # Add more assertions based on the expected state of UE with ID 4

    print(f"Test passed for UE {ue_id_to_test}: {ue_info}")

# Run the test
test_network_state_functionality()