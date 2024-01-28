# debug_utils.py inside utills folder and the role is manage of the debug massages
import os
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() in ('true', '1', 't')

def debug_print(message):
    if DEBUG_MODE:
        print(message)