# init_gNodeB.py  // this file located in network directory
# Initialization of gNodeBs
import os
import json
from .gNodeB import gNodeB

def load_json_config(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def initialize_gNodeBs(gNodeBs_config, db_manager):
    gNodeBs = {}
    for gNodeB_data in gNodeBs_config['gNodeBs']:
        gnodeb = gNodeB(**gNodeB_data)
        gNodeBs[gnodeb.ID] = gnodeb
        point = gnodeb.serialize_for_influxdb()  # Serialize for InfluxDB
        db_manager.insert_data(point)  # Insert the Point object directly
    return gNodeBs