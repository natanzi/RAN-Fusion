import unittest
from unittest.mock import patch, MagicMock
from network.gNodeB_manager import gNodeBManager
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

class TestGNodeBManager(unittest.TestCase):
    def setUp(self):
        # Initialize gNodeBManager with a specified base directory
        self.gNodeB_manager = gNodeBManager(base_dir="your_base_dir_here")
        # Mock the database manager to avoid actual database operations during tests
        self.gNodeB_manager.db_manager = MagicMock()

    def test_gNodeB_names_and_count(self):
        # Initialize gNodeBs to load them into memory and simulate database insertion
        self.gNodeB_manager.initialize_gNodeBs()

        # Get gNodeB names from the configuration
        configured_gNodeB_names = [gNodeB['gnodeb_id'] for gNodeB in self.gNodeB_manager.gNodeBs_config['gNodeBs']]

        # Get gNodeB names from memory
        memory_gNodeB_names = list(self.gNodeB_manager.gNodeBs.keys())

        # Assuming a method in DatabaseManager to get all gNodeB names from the database
        # For this example, we'll mock this method
        self.gNodeB_manager.db_manager.get_all_gNodeB_names.return_value = memory_gNodeB_names

        # Get gNodeB names from the database (mocked)
        database_gNodeB_names = self.gNodeB_manager.db_manager.get_all_gNodeB_names()

        # Check if the count of gNodeBs matches
        self.assertEqual(len(configured_gNodeB_names), len(memory_gNodeB_names), "Mismatch in gNodeB count between configuration and memory.")
        self.assertEqual(len(configured_gNodeB_names), len(database_gNodeB_names), "Mismatch in gNodeB count between configuration and database.")

        # Check if the gNodeB names match
        self.assertCountEqual(configured_gNodeB_names, memory_gNodeB_names, "Mismatch in gNodeB names between configuration and memory.")
        self.assertCountEqual(configured_gNodeB_names, database_gNodeB_names, "Mismatch in gNodeB names between configuration and database.")

if __name__ == '__main__':
    unittest.main()