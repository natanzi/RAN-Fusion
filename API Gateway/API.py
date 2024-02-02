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

app = Flask(__name__)
lock = threading.Lock()

# Function to log UE updates
def log_ue_update(message):
    with open('ue_updates.log', 'a') as log_file:
        log_file.write(message + "\n")

@app.route('/add_ue', methods=['POST'])
def add_ue():
    data = request.json
    # Validate required fields are present
    required_fields = ['ue_id', 'service_type', 'sector_id']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

    ue_id = data['ue_id']
    service_type = data['service_type']
    sector_id = data['sector_id']
    # Further validation can be added here (e.g., check if sector_id is valid)
    try:
        sector = Sector.get_sector_by_id(sector_id)
        if not sector:
            return jsonify({'error': 'Sector not found'}), 404

        ue_config = {
            'ue_id': ue_id,
            'service_type': service_type,
            # Include other necessary parameters for UE initialization here
        }
        ue = UE(config=ue_config, ue_id=ue_id, service_type=service_type)

        with lock:  # Ensure thread safety
            success = sector.add_ue(ue)

        if success:
            log_ue_update(f"UE ID: {ue_id}, Service Type: {service_type}, Sector ID: {sector_id}, Cell ID: {ue.ConnectedCellID}, gNodeB ID: {ue.gNodeB_ID}")
            return jsonify({'message': f'UE {ue_id} added successfully to sector {sector_id}'}), 200
        else:
            return jsonify({'error': 'Failed to add UE to sector'}), 500
    except Exception as e:
        return jsonify({'error': 'An error occurred while adding UE'}), 500

@app.route('/remove_ue', methods=['POST'])
def remove_ue():
    data = request.json
    # Validate required fields are present
    required_fields = ['ue_id', 'sector_id']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

    ue_id = data['ue_id']
    sector_id = data['sector_id']
    try:
        sector = Sector.get_sector_by_id(sector_id)
        if not sector:
            return jsonify({'error': 'Sector not found'}), 404

        with lock:  # Ensure thread safety
            success = sector.remove_ue(ue_id)

        if success:
            log_ue_update(f"UE ID: {ue_id} removed from Sector ID: {sector_id}")
            return jsonify({'message': f'UE {ue_id} removed successfully from sector {sector_id}'}), 200
        else:
            return jsonify({'error': 'Failed to remove UE from sector'}), 500
    except Exception as e:
        return jsonify({'error': 'An error occurred while removing UE'}), 500

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

if __name__ == '__main__':
    app.run(debug=True)