# This is API.py which is located in API Gateway folder to have control over all nodes
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) 
from network.ue import UE 
from network.sector import Sector
from flask import Flask, request, jsonify
from threading import Lock
import traceback
import threading
import json
from network.sector_manager import all_sectors
from database.database_manager import DatabaseManager


app = Flask(__name__)
lock = Lock()

print(all_sectors)
print(f"Length of all_sectors in API: {len(all_sectors)}")

# Function to log UE updates
def log_ue_update(message):
    with open('ue_updates.log', 'a') as log_file:
        log_file.write(message + "\n")

#########################################################################################################
@app.route('/add_ue', methods=['POST'])
def add_ue():
    data = request.json
    print("Received data:", data)  # Log received data

    # Validate required fields are present
    required_fields = ['ue_id', 'service_type', 'sector_id']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        print(f"Missing required fields: {', '.join(missing_fields)}")  # Log missing fields
        return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

    ue_id = data['ue_id']
    service_type = data['service_type']
    sector_id = data['sector_id']

    # Validate sector_id format (example validation, adjust as needed)
    if not isinstance(sector_id, str) or len(sector_id) < 5:  # Example validation condition
        print(f"Invalid sector_id format: {sector_id}")
        return jsonify({'error': 'Invalid sector_id format'}), 400

    # Extract ue_config from the request data, excluding known fields
    ue_config = {key: value for key, value in data.items() if key not in ['ue_id', 'service_type', 'sector_id']}

    print(f"Processing UE with ID: {ue_id} for sector: {sector_id}")  # Log UE ID and sector ID

    # Attempt to retrieve the sector
    try:
        sector = Sector.get_sector_by_id(sector_id)
        if not sector:
            print(f"Sector with ID: {sector_id} not found")  # Log sector not found
            return jsonify({'error': 'Sector not found'}), 404
        print(f"Before adding UE, Sector {sector_id} remaining_capacity: {sector.remaining_capacity}, current_load: {sector.current_load}")
    except Exception as e:
        print(f"Error getting sector: {e}")  # Log exception when retrieving sector
        return jsonify({'error': 'An error occurred while retrieving sector'}), 500

    # Separate try/except for UE creation
    try:
        ue = UE(config=ue_config, ue_id=ue_id, service_type=service_type)
        print(f"Initialized UE object: {ue}")  # Print the UE object after creation
    except Exception as e:
        print(f"Error creating UE: {e}")  # Log exception when creating UE
        return jsonify({'error': 'An error occurred while creating UE'}), 500

    # Separate try/except for adding UE to sector
    try:
        with lock:  # Ensure thread safety
            success = sector.add_ue(ue)
            if success:
                print(f"After adding UE, Sector {sector_id} remaining_capacity: {sector.remaining_capacity}, current_load: {sector.current_load}")
                log_ue_update(f"UE ID: {ue_id}, Service Type: {service_type}, Sector ID: {sector_id}, Cell ID: {ue.ConnectedCellID}, gNodeB ID: {ue.gNodeB_ID}")
                print(f"UE {ue_id} added successfully to sector {sector_id}")  # Log success
                return jsonify({'message': f'UE {ue_id} added successfully to sector {sector_id}'}), 200
            else:
                print(f"Failed to add UE {ue_id} to sector {sector_id}")  # Log failure to add UE
                return jsonify({'error': 'Failed to add UE to sector'}), 500
    except Exception as e:
        print(f"Error adding UE to sector: {e}")  # Log exception when adding UE to sector
        return jsonify({'error': 'An error occurred while adding UE to sector'}), 500

#########################################################################################################
@app.route('/remove_ue', methods=['POST'])
def remove_ue():
    data = request.json
    print("Received request to remove UE:", data)
    required_fields = ['ue_id', 'sector_id']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400
    
    ue_id = data['ue_id']
    sector_id = data['sector_id']
    
    # Validate sector_id and ue_id formats (example validation, adjust as needed)
    if not isinstance(sector_id, str) or len(sector_id) < 5:
        return jsonify({'error': 'Invalid sector_id format'}), 400
    if not isinstance(ue_id, str) or len(ue_id) < 3:
        return jsonify({'error': 'Invalid ue_id format'}), 400
    
    db_manager = DatabaseManager()  # Instantiate your DatabaseManager
    
    try:
        # Ensure thread safety
        with lock:
            # Attempt to retrieve the sector and remove the UE
            print(f"Attempting to find sector with ID: {sector_id} in all_sectors: {all_sectors}")
            sector = Sector.get_sector_by_id(sector_id)
            if not sector:
                return jsonify({'error': 'Sector not found'}), 404
            
            # Assuming Sector class has a method remove_ue that returns True if removal was successful
            success = sector.remove_ue(ue_id)
            if success:
                # Additionally, remove the UE's state from InfluxDB
                db_manager.remove_ue_state(ue_id, sector_id)  # This method needs to be implemented in DatabaseManager
                log_ue_update(f"UE ID: {ue_id} removed from Sector ID: {sector_id}")
                return jsonify({'message': f'UE {ue_id} removed successfully from sector {sector_id}'}), 200
            else:
                return jsonify({'error': 'Failed to remove UE from sector'}), 500
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An error occurred while removing UE'}), 500
#########################################################################################################
if __name__ == '__main__':
    app.run(debug=True)
    
@app.route('/update_ue', methods=['POST'])
def update_ue():
    data = request.json
    # Validate that ue_id is provided
    if 'ue_id' not in data:
        return jsonify({'error': 'Missing ue_id in request'}), 400

    ue_id = data['ue_id']

    # Validate that there are parameters to update
    if len(data) <= 1:  # Only ue_id is present, no parameters to update
        return jsonify({'error': 'No parameters provided for update'}), 400

    try:
        ue = UE.get_ue_instance_by_id(ue_id)
        if not ue:
            return jsonify({'error': 'UE not found'}), 404

        # Remove 'ue_id' from the data as it's not a parameter to be updated
        data.pop('ue_id', None)

        # Update UE parameters
        ue.update_parameters(**data)

        return jsonify({'message': f'UE {ue_id} updated successfully'}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An error occurred while updating UE'}), 500
#########################################################################################################
if __name__ == '__main__':
    print("Starting API server...")
    print(f"Available sectors at API start: {list(all_sectors.keys())}")
    app.run(debug=True)