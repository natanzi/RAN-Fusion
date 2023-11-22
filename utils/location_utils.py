#Functions for handling location-based calculations.
# Assuming this function is added to 'utils/location_utils.py'

def get_nearest_gNodeB(ue_location, gNodeBs):
    ue_lat, ue_lon = ue_location
    nearest_gNodeB = None
    min_distance = float('inf')

    for gNodeB in gNodeBs:
        distance = calculate_distance(ue_lat, ue_lon, gNodeB.Latitude, gNodeB.Longitude)
        if distance < min_distance:
            min_distance = distance
            nearest_gNodeB = gNodeB

    return nearest_gNodeB, min_distance

def get_ue_location_info(ue, gNodeBs, cells):
    ue_location = ue.Location
    neighbors_info = []

    # Find the nearest gNodeB
    nearest_gNodeB, distance_to_nearest_gNodeB = get_nearest_gNodeB(ue_location, gNodeBs)

    # Calculate distance to each cell of the nearest gNodeB
    for cell in nearest_gNodeB.Cells:
        cell_location = (cell.Latitude, cell.Longitude)  # Assuming cells have Latitude and Longitude attributes
        distance_to_cell = calculate_distance(ue_location[0], ue_location[1], cell_location[0], cell_location[1])
        neighbors_info.append({
            'gNodeB_ID': nearest_gNodeB.ID,
            'Cell_ID': cell.ID,
            'Distance': distance_to_cell
        })

    # Sort the information by distance
    neighbors_info.sort(key=lambda x: x['Distance'])

    # Return the UE's location, the nearest gNodeB, and the sorted list of neighboring cells by distance
    return {
        'UE_Location': ue_location,
        'Nearest_gNodeB': {
            'ID': nearest_gNodeB.ID,
            'Distance': distance_to_nearest_gNodeB
        },
        'Neighboring_Cells_Info': neighbors_info
    }