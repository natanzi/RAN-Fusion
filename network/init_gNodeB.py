#init_gNodeB.py  // this file located in network directory
# Initialization of gNodeBs
import os
import json
from .gNodeB import gNodeB  # Relative import

def load_json_config(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def initialize_gNodeBs(gNodeBs_config):
    # Initialize gNodeBs using the provided configuration
    # Change from list to dictionary with gNodeB_id as keys
    gNodeBs = {gNodeB_data['gnodeb_id']: gNodeB(**gNodeB_data) for gNodeB_data in gNodeBs_config['gNodeBs']}
    return gNodeBs