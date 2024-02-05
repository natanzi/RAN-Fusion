import unittest
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
                {
                    'gnodeb_id': 'gNodeB2', 
                    'latitude': 30.0, 
                    'longitude': 40.0, 
                    'coverageRadius': 1500, 
                    'power': 600, 
                    'frequency': 1900, 
                    'bandwidth': 150, 
                    'location': [30.0, 40.0],  # Added location parameter
                    'region': 'SomeRegion2', 
                    'maxUEs': 150, 
                    'cellCount': 4, 
                    'sectorCount': 4, 
                    'handoverMargin': 6, 
                    'handoverHysteresis': 3, 
                    'timeToTrigger': 60, 
                    'interFreqHandover': False, 
                    'xnInterface': False, 
                    'sonCapabilities': {'someCapability': False}, 
                    'loadBalancingOffset': 15, 
                    'cellIds': ['cell4', 'cell5', 'cell6', 'cell7'], 
                    'sectorIds': ['sector4', 'sector5', 'sector6', 'sector7']
                }
            ]
        }

    def test_initialize_gNodeBs(self):
        # Initialize gNodeBs based on the mocked configuration
        self.gNodeB_manager.initialize_gNodeBs()
        # Ensure all gNodeBs are created
        self.assertIn('gNodeB1', self.gNodeB_manager.gNodeBs)
        self.assertIn('gNodeB2', self.gNodeB_manager.gNodeBs)
        # Verify configuration parameters of a gNodeB
        gNodeB1 = self.gNodeB_manager.get_gNodeB('gNodeB1')
        self.assertEqual(gNodeB1.ID, 'gNodeB1')
        self.assertEqual(gNodeB1.Location, [10.0, 20.0])  # Verify location

    def test_add_gNodeB(self):
        # Correctly formatted gNodeB data including the location parameter
        gNodeB_data = {
            'gnodeb_id': 'gNodeB3', 
            'latitude': 50.0, 
            'longitude': 60.0, 
            'coverageRadius': 2000, 
            'power': 700, 
            'frequency': 2000, 
            'bandwidth': 200, 
            'location': [50.0, 60.0],  # Added location parameter
            'region': 'SomeRegion3', 
            'maxUEs': 200, 
            'cellCount': 5, 
            'sectorCount': 5, 
            'handoverMargin': 7, 
            'handoverHysteresis': 4, 
            'timeToTrigger': 70, 
            'interFreqHandover': True, 
            'xnInterface': True, 
            'sonCapabilities': {'someCapability': True}, 
            'loadBalancingOffset': 20, 
            'cellIds': ['cell8', 'cell9', 'cell10', 'cell11', 'cell12'], 
            'sectorIds': ['sector8', 'sector9', 'sector10', 'sector11', 'sector12']
        }
        self.gNodeB_manager.add_gNodeB(gNodeB_data)
        # Check if the gNodeB is added
        self.assertIn('gNodeB3', self.gNodeB_manager.gNodeBs)
        self.assertIsNotNone(self.gNodeB_manager.get_gNodeB('gNodeB3'))

if __name__ == '__main__':
    unittest.main()