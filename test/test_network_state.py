#to insure that network state class is working
#test_network_state.py located in test folder
import unittest
from network.network_state import NetworkState  # Adjust the import path as necessary

class TestNetworkState(unittest.TestCase):

    def setUp(self):
        # Set up a NetworkState instance and any other necessary objects
        self.network_state = NetworkState()

    def test_some_method(self):
        # Test a method of NetworkState
        # For example, if there's a method that adds a node:
        result = self.network_state.add_node(some_parameters)
        self.assertEqual(result, expected_result)

    # Add more test methods for other NetworkState methods

if __name__ == '__main__':
    unittest.main()