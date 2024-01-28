# This is the config.py in Config_files directory to load all JSON configs
#Creating a Config class to encapsulate the different configuration dictionaries

import os
import json

class Config:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.gNodeBs_config = self.load_json_config('gNodeB_config.json')
        self.cells_config = self.load_json_config('cell_config.json')
        self.sectors_config = self.load_json_config('sector_config.json')
        self.ue_config = self.load_json_config('ue_config.json')
        self.debug_mode = True  # Set to False to disable debug print messages

    def load_json_config(self, filename):
        file_path = os.path.join(self.base_dir, 'Config_files', filename)
        with open(file_path, 'r') as file:
            return json.load(file)
        