# debug_utils.py inside utill folder and the role is manage of the debug massages

def debug_print(message, config):
    if config.debug_mode:
        print(message)