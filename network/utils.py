# utils.py in the network directory
import random
import math

def random_location_within_radius(center_lat, center_lon, radius_km):

    x = random.uniform(-radius_km, radius_km)
    y = random.uniform(-radius_km, radius_km)

    lat = center_lat + x/110.574
    lon = center_lon + y/111.320*math.cos(center_lat)

    return lat, lon