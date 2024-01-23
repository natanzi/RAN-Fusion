#Functions for calculating signal strength based on distance and other factors.
# signal_strength.py

from math import radians, cos, sin, asin, sqrt

# You can import the haversine function from network_metrics.py if it's in the same directory
# or adjust the import path accordingly if it's located elsewhere.

def calculate_signal_strength(ue_location, gNodeB_location, gNodeB_coverage_radius):
    """
    Calculate the signal strength based on the distance from the user equipment (UE) to the gNodeB
    and other factors such as the coverage radius of the gNodeB.

    :param ue_location: Tuple representing the latitude and longitude of the UE.
    :param gNodeB_location: Tuple representing the latitude and longitude of the gNodeB.
    :param gNodeB_coverage_radius: The coverage radius of the gNodeB in kilometers.
    :return: Signal strength as a value between 0 and 100.
    """
    # Calculate the distance between the UE and the gNodeB
    distance_to_gNodeB = haversine(ue_location[1], ue_location[0], gNodeB_location[1], gNodeB_location[0])

    # Adjust the signal strength calculation to return a value between 0 and 100
    # The signal strength is 100 at the gNodeB and decreases linearly to 0 at the edge of the coverage radius
    signal_strength = max(0, 100 * (1 - (distance_to_gNodeB / gNodeB_coverage_radius)))
    
    # You can include other factors in the calculation if needed
    # For example, you might want to include environmental factors, gNodeB power, etc.

    return signal_strength

# You can include additional helper functions or classes as needed.