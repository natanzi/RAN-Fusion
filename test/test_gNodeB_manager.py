import unittest
from unittest.mock import patch, call  # Import call here
from network.gNodeB_manager import gNodeBManager
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from network.gNodeB_manager import gNodeBManager

class TestGNodeBManager(unittest.TestCase):
    def setUp(self):
        # Initialize gNodeBManager with a specified base directory
        self.gNodeB_manager = gNodeBManager(base_dir=os.path.dirname(__file__))
        # Mock the loading of gNodeB configurations to include specific gNodeB IDs
        self.gNodeB_manager.gNodeBs_config = {
            'gNodeBs': [
                {'gnodeb_id': 'W1140'},  # Example configuration for W1140
                {'gnodeb_id': 'W1320'},  # Example configuration for W1320
                {'gnodeb_id': 'W2018'},  # Example configuration for W2018
            ]
        }

    @patch('network.gNodeB_manager.DatabaseManager')
    def test_initialize_gNodeBs(self, mock_db_manager):
        self.gNodeB_manager.initialize_gNodeBs()
        # Verify the number of gNodeBs matches the configuration
        self.assertEqual(len(self.gNodeB_manager.gNodeBs), len(self.gNodeB_manager.gNodeBs_config['gNodeBs']))
        # Ensure the specific gNodeBs are created in memory
        for gNodeB_id in ['W1140', 'W1320', 'W2018']:
            self.assertIn(gNodeB_id, self.gNodeB_manager.gNodeBs)
        # Verify that the database insertion was attempted for each specified gNodeB
        expected_calls = [call(point) for point in [gNodeB['gnodeb_id'] for gNodeB in self.gNodeB_manager.gNodeBs_config['gNodeBs']]]
        mock_db_manager.return_value.insert_data.assert_has_calls(expected_calls, any_order=True)

    # Additional test cases as needed

if __name__ == '__main__':
    unittest.main()