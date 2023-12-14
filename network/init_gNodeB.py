#init_gNodeB.py  // this file located in network directory
# Initialization of gNodeBs
import os
import json
from .gNodeB import gNodeB  # Relative import

def load_json_config(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def initialize_gNodeBs(gNodeBs_config, db_manager):
    gNodeBs = {}
    for gNodeB_data in gNodeBs_config['gNodeBs']:
        gnodeb = gNodeB(**gNodeB_data)
        gNodeBs[gnodeb.ID] = gnodeb
        # Serialize and write to InfluxDB
        point = gnodeb.serialize_for_influxdb()
        db_manager.insert_data("gnodeb_metrics", point.tags, point.fields, point.time)
    return gNodeBs