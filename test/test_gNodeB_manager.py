import unittest
from unittest.mock import patch
from network.gNodeB_manager import gNodeBManager
import sys
import os

# Adjust the system path to ensure the test can import modules from the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

class TestGNodeBManager(unittest.TestCase):
    def setUp(self):
        # Initialize gNodeBManager with a specified base directory
        self.gNodeB_manager = gNodeBManager(base_dir=os.path.dirname(__file__))
        # Mock the loading of gNodeB configurations if necessary
        self.gNodeB_manager.gNodeBs_config = {
            'gNodeBs': [
                {
                    'gnodeb_id': 'gNodeB1',
                    'latitude': 10.0,
                    'longitude': 20.0,
                    'coverageRadius': 1000,
                    'power': 500,
                    'frequency': 1800,
                    'bandwidth': 100,
                    'location': [10.0, 20.0],  # Added location parameter
                    'region': 'SomeRegion1',
                    'maxUEs': 100,
                    'cellCount': 3,
                    'sectorCount': 3,
                    'handoverMargin': 5,
                    'handoverHysteresis': 2,
                    'timeToTrigger': 50,
                    'interFreqHandover': True,
                    'xnInterface': True,
                    'sonCapabilities': {'someCapability': True},
                    'loadBalancingOffset': 10,
                    'cellIds': ['cell1', 'cell2', 'cell3'],
                    'sectorIds': ['sector1', 'sector2', 'sector3']
                },
                # Add other gNodeB configurations as needed
            ]
        }

    @patch('network.gNodeB_manager.DatabaseManager')
    def test_initialize_gNodeBs(self, mock_db_manager):
        self.gNodeB_manager.initialize_gNodeBs()
        # Verify the number of gNodeBs matches the configuration
        self.assertEqual(len(self.gNodeB_manager.gNodeBs), len(self.gNodeB_manager.gNodeBs_config['gNodeBs']))
        # Ensure all gNodeBs are created
        self.assertIn('gNodeB1', self.gNodeB_manager.gNodeBs)
        # Verify configuration parameters of a gNodeB
        gNodeB1 = self.gNodeB_manager.get_gNodeB('gNodeB1')
        self.assertEqual(gNodeB1.ID, 'gNodeB1')
        self.assertEqual(gNodeB1.Location, [10.0, 20.0])
        # Verify that the database insertion was attempted for each gNodeB
        self.assertEqual(mock_db_manager.return_value.insert_data.call_count, len(self.gNodeB_manager.gNodeBs_config['gNodeBs']))

    # Additional test cases as needed

if __name__ == '__main__':
    unittest.main()