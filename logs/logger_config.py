#logger_config.py for define all log in log folder
import logging
import os
import json
import gzip
from datetime import datetime
from logging.handlers import RotatingFileHandler
from concurrent.futures import ThreadPoolExecutor

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "level": record.levelname,
            "timestamp": datetime.utcfromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S'),
            "message": record.getMessage()
        }
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)
        return json.dumps(log_record)

def setup_logger(name, log_file, level=logging.INFO, max_log_size=10 * 1024 * 1024, backup_count=5):
    """Function to set up a logger with asynchronous and buffered logging."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create log directory if it doesn't exist
    log_directory = os.path.dirname(log_file)
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    # Create a rotating file handler with asynchronous logging
    file_handler = RotatingFileHandler(log_file, maxBytes=max_log_size, backupCount=backup_count)
    file_handler.setLevel(level)
    formatter = JsonFormatter()

    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)

    return logger

def compress_log_file(log_file):
    """Compress the log file using gzip, if it exists, after log rotation."""
    log_file_backup = log_file + ".1"  # Assuming 1 is the first backup file

    if os.path.exists(log_file_backup):
        with open(log_file_backup, 'rb') as log:
            with gzip.open(log_file_backup + '.gz', 'wb') as compressed_log:
                compressed_log.writelines(log)

        # Remove the original log file (backup)
        os.remove(log_file_backup)

# Create a dictionary to hold loggers and their respective log files
loggers = {
    'ue_logger': 'logs/ue_logger.log',
    'cell_logger': 'logs/cell_logger.log',
    'gnodeb_logger': 'logs/gnodeb_logger.log',
    'cell_load_logger': 'logs/cell_load.log',
    'traffic_update': 'logs/traffic_update.log',
    'database_logger': 'logs/database_logger.log'
}

# Set up loggers for all components
with ThreadPoolExecutor(max_workers=1) as executor:
    for logger_name, log_file in loggers.items():
        loggers[logger_name] = setup_logger(logger_name, log_file)
        # Schedule log compression for older log files (e.g., once a day)
        executor.submit(compress_log_file, log_file)

