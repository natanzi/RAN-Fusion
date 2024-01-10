# this is network_delay.py in network folder
class NetworkDelay:

    def __init__(self, base_delay=10):
        self.base_delay = base_delay
        # Additional attributes can be added here if needed

    def calculate_delay(self, cell_load):
        # Logic to calculate network delay remains unchanged
        load_factor = 1 + cell_load / 100
        return self.base_delay * load_factor