#init_gNodeB.py  // this file located in network directory
# Initialization of gNodeBs
import os
import json
from .gNodeB import gNodeB  # Relative import

def load_json_config(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def initialize_gNodeBs():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_dir = os.path.join(base_dir, 'Config_files')

    gNodeBs_config = load_json_config(os.path.join(config_dir, 'gNodeB_config.json'))

    # Initialize gNodeBs
    gNodeBs = [gNodeB(**gNodeB_data) for gNodeB_data in gNodeBs_config['gNodeBs']]
    return gNodeBs