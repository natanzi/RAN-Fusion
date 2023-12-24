import random

class UserEquipment:
    def __init__(self, battery_capacity_mAH, discharge_rate, power_amplifier_efficiency, max_transmit_power_dBm):
        # Initialize parameters with a random battery level
        self.battery_capacity = battery_capacity_mAH  # in mAH
        self.battery_level = random.uniform(50, 100)  # Random initial battery level between 10% and 100%
        self.discharge_rate = discharge_rate  # as a percentage per minute
        self.power_amplifier_efficiency = power_amplifier_efficiency  # in percentage
        self.max_transmit_power = max_transmit_power_dBm  # in dBm
        self.power_model = {'RF': 0, 'Baseband': 0, 'Processor': 0, 'Display': 0}  # Power usage of each component

    def update_power_model(self, RF, Baseband, Processor, Display):
        # Update the power consumption of each component
        self.power_model['RF'] = RF
        self.power_model['Baseband'] = Baseband
        self.power_model['Processor'] = Processor
        self.power_model['Display'] = Display

    def calculate_power_consumption(self):
        # Calculate total power consumption
        total_power = sum(self.power_model.values())
        return total_power * (1 - self.power_amplifier_efficiency / 100)

    def update_battery_level(self, time_minutes):
        # Update battery level based on usage
        power_consumption = self.calculate_power_consumption()
        self.battery_level -= (power_consumption * self.discharge_rate * time_minutes) / self.battery_capacity
        self.battery_level = max(self.battery_level, 0)  # Battery level should not go below 0

    def get_battery_level(self):
        # Return the current battery level in percentage
        return self.battery_level

# Example usage
battery_capacity_range = (2000, 4000)  # mAH
discharge_rate_range = (0.4, 0.6)  # percentage per minute
amplifier_efficiency_range = (25, 35)  # percentage
max_transmit_power_range = (15, 25)  # dBm

# Creating a single UE instance as an example
ue = UserEquipment(random.uniform(*battery_capacity_range), random.uniform(*discharge_rate_range), 
        random.uniform(*amplifier_efficiency_range), random.uniform(*max_transmit_power_range))

# Update UE usage (e.g., for 10 minutes of operation with specific power model settings)
ue.update_power_model(RF=5, Baseband=3, Processor=2, Display=1)
ue.update_battery_level(10)

# Get the current battery level
current_battery_level = ue.get_battery_level()
# current_battery_level now holds the battery level in percentage
