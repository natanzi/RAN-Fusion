# debug_utils.py inside utills folder and the role is manage of the debug massages
import os
DEBUG_MODE = False

def debug_print(message):
    if DEBUG_MODE:
        print(message)