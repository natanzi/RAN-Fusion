# network_delay.py inside the network folder
class NetworkDelay:
    def __init__(self, base_delay=10):
        """
        Initialize the NetworkDelay class with a base delay.
        :param base_delay: The base network delay without any load (in milliseconds).
        """
        self.base_delay = base_delay

    def calculate_delay(self, cell_load):
        """
        Calculate the network delay based on the cell load.
        :param cell_load: The current load of the cell (as a percentage).
        :return: The calculated network delay (in milliseconds).
        """
        # Assuming delay increases non-linearly with load; you can adjust the formula as needed
        load_factor = 1 + (cell_load / 100)**2  # Example: quadratic increase
        return self.base_delay * load_factor

    def apply_delay_to_throughput(self, ue_throughput, cell_load):
        """
        Simulate the effect of network delay on UE throughput.
        :param ue_throughput: The current throughput of the UE (in Mbps).
        :param cell_load: The current load of the cell (as a percentage).
        :return: The adjusted UE throughput (in Mbps).
        """
        network_delay = self.calculate_delay(cell_load)
        # This is a simple model where throughput is inversely proportional to delay
        # The formula can be adjusted based on the desired simulation behavior
        if network_delay > 0:
            adjusted_throughput = ue_throughput / (1 + (network_delay / 1000))
        else:
            adjusted_throughput = ue_throughput
        return adjusted_throughput