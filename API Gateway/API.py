import sys
import os
# Calculate the path to the root of the project
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from flask import Flask, request, jsonify
from network.ue import UE
from network.sector import Sector
from threading import Lock
import traceback
import threading

app = Flask(__name__)
lock = threading.Lock()

# Function to log UE updates
def log_ue_update(message):
    with open('ue_updates.log', 'a') as log_file:
        log_file.write(message + "\n")

@app.route('/add_ue', methods=['POST'])
def add_ue():
    data = request.json
    ue_id = data['ue_id']
    service_type = data['service_type']
    sector_id = data['sector_id']
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
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/remove_ue', methods=['POST'])
def remove_ue():
    data = request.json
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
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/update_ue', methods=['POST'])
def update_ue():
    data = request.json
    ue_id = data['ue_id']
    try:
        ue = UE.get_ue_instance_by_id(ue_id)
        if not ue:
            return jsonify({'error': 'UE not found'}), 404

        for param, value in data.items():
            if hasattr(ue, param) and param != 'ue_id':  # Prevent changing the UE ID
                setattr(ue, param, value)
        log_ue_update(f"UE ID: {ue_id} updated successfully")
        return jsonify({'message': f'UE {ue_id} updated successfully'}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)