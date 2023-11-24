#this is the config_load.py in Config_files directory to loading all json config
import json
import os

def load_json_config(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def load_all_configs(base_dir):
    config_dir = os.path.join(base_dir, 'Config_files')

    gNodeB_json_path = os.path.join(config_dir, 'gNodeB_config.json')
    cell_json_path = os.path.join(config_dir, 'cell_config.json')
    ue_json_path = os.path.join(config_dir, 'ue_config.json')

    gNodeBs_config = load_json_config(gNodeB_json_path)
    cells_config = load_json_config(cell_json_path)
    ue_config = load_json_config(ue_json_path)

    return gNodeBs_config, cells_config, ue_config
