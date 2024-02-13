# this is network_delay.py in network folder #Accounts for different traffic types by adjusting the delay based on the specific QoS requirements of each traffic type.
#Incorporates a non-linear growth factor for the delay as the cell load increases, providing a more realistic simulation of network behavior under load.
#Adds random variability within ±10% of the calculated delay to simulate the unpredictable nature of real-world network conditions.
#Ensures that the delay does not exceed a specified maximum value, reflecting the practical limits of network performance degradation.
############################################################################################################################################################################################
##  Non-linear Load Factor Calculation: The delay calculation starts with a non-linear load factor based on the cell load. 
#   This is achieved through the expression math.exp(cell_load / 100) - 1. As the cell load increases, this factor grows non-linearly,
#   meaning the increase in delay is more pronounced at higher loads. This reflects a more realistic simulation of network behavior under load,
#   where the impact on delay becomes significantly higher as the network approaches its capacity.##  Adjustment for Traffic Type: The method further
#   refines the delay calculation by adjusting for the type of traffic (voice, video, game, IoT, data), each having different QoS (Quality of Service) requirements.
#   This adjustment is made through the qos_factor, which modifies the delay based on the sensitivity of the traffic type to delays. While this step doesn't directly relate to 
#   the increase in delay due to higher cell load, it adds another layer of realism by recognizing that not all traffic is affected by network conditions in the same way.
#   Random Variability: To simulate the unpredictable nature of real-world network conditions, the method introduces random variability within ±10% of the calculated delay.
#   This variability is applied after the initial delay calculation, meaning the base delay influenced by cell load and traffic type can either slightly increase or decrease, 
#   adding a stochastic element to the delay simulation. Maximum Delay Limit: Finally, the method ensures that the calculated delay does not exceed a specified maximum value (max_delay).
#   This represents the practical limits of network performance degradation, ensuring that the simulation remains within realistic bounds.
#
#   In summary, as the UE throughput increases,leading to a higher cell load, the calculate_delay method ensures that the network delay also increases in a non-linear fashion, reflecting 
##   a realistic simulation of how networks behave under load. This increase in delay is further nuanced by adjustments for traffic type and random variability, providing a comprehensive approach to simulating network delay.
########################################################################################################################################################################################
import math
import random
from database.database_manager import DatabaseManager

class NetworkDelay:

    def __init__(self, base_delay=10, max_delay=100):
        self.base_delay = base_delay
        self.max_delay = max_delay

    def calculate_delay(self, cell_load, traffic_type='data'):

        """
        Calculate network delay based on cell load and traffic type.
        Incorporates non-linear growth, random variability, and adjusts for traffic type.
        
        :param cell_load: The current load of the cell as a percentage.
        :param traffic_type: The type of traffic, affecting QoS.
        :return: The calculated network delay.
        """
        # Non-linear load factor calculation
        load_factor = math.exp(cell_load / 100) - 1
        
        # Adjust delay based on traffic type
        qos_factor = 1.0  # Default QoS factor

        if traffic_type == 'voice':
            qos_factor = 0.8  # Voice traffic might be more sensitive to delay
        elif traffic_type == 'video':
            qos_factor = 0.9  # Video traffic has slightly less sensitivity compared to voice
        elif traffic_type == 'game':
            qos_factor = 0.7  # Gaming traffic is very sensitive to delay
        elif traffic_type == 'iot':
            qos_factor = 1.1  # IoT traffic might be less sensitive to delay
        elif traffic_type == 'data':
            qos_factor = 1.0  # Default QoS factor for data traffic
        
        # Calculate preliminary delay
        delay = self.base_delay * (1 + load_factor) * qos_factor
        
        # Add random variability within ±10% of the current delay
        variability_factor = random.uniform(-0.1, 0.1)
        delay += delay * variability_factor
        
        # Ensure delay does not exceed max_delay
        delay = min(delay, self.max_delay)
        
        return delay

    # Placeholder for a method that adjusts base_delay based on UE throughput feedback
    # This method would need more context about how throughput data is collected and analyzed
    def adjust_for_throughput(self, throughput):
        """
        Adjust the base delay based on UE throughput feedback.The adjust_for_throughput method in your NetworkDelay class is designed as a placeholder to incorporate adjustments to the network delay based on User Equipment (UE) throughput feedback. This method suggests an intention to dynamically adjust network performance parameters in response to real or simulated network conditions, specifically the throughput experienced by UEs.         
        :param throughput: Some metric or calculation representing UE throughput.
        
        1. Understand UE Throughput Feedback
        First, you need to understand how throughput data for UEs is collected and analyzed within your system. This involves knowing:

        Data Collection: How and where in the system the UE throughput data is being collected. This could be simulated data in a test environment or real data in a live network.
        Analysis: How this data is analyzed or processed to derive meaningful insights. For example, you might calculate average throughput, peak throughput, or detect patterns of throughput changes over time.
        2. Define Adjustment Logic
        Based on the insights from the throughput data, define the logic for how the base delay should be adjusted. Consider the following:

        Thresholds: Define throughput thresholds that trigger adjustments in the base delay. For example, if throughput drops below a certain level, it might indicate congestion, leading to an increase in the base delay.
        Adjustment Strategy: Decide how the base delay will be adjusted. This could involve a linear adjustment, a percentage increase/decrease, or more complex algorithms that take into account additional factors like traffic type, time of day, or historical performance data
        """
        pass  # Implementation would depend on specific throughput metrics and goals
