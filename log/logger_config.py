#logger_config.py for define all log in log folder
import logging
import os
from datetime import datetime

def setup_logger(name, log_file, level=logging.INFO):
    """Function to set up a logger."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create log directory if it doesn't exist
    log_directory = os.path.dirname(log_file)
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    # Create file handler and set level and formatter
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler.setFormatter(formatter)

    # Add file handler to logger
    logger.addHandler(file_handler)

    return logger

# Set up loggers for UE, Cell, and gNodeB
ue_logger = setup_logger('ue_logger', 'log/ue_logger.log')
cell_logger = setup_logger('cell_logger', 'log/cell_load.log', 'INFO')  # Correct file path
gnodeb_logger = setup_logger('gnodeb_logger', 'log/gnodeb_logger.log')
