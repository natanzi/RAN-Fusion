from flask import Flask, request, jsonify
from network.ue import UE
from network.sector import Sector
from threading import Lock
import traceback

app = Flask(__name__)
lock = Lock()

@app.route('/add_ue', methods=['POST'])
def add_ue():
    data = request.json
    ue_id = data['ue_id']
    service_type = data['service_type']
    sector_id = data['sector_id']
    try:
        # Assuming Sector.get_sector_by_id is a method that retrieves a sector by its ID
        # If it doesn't exist, you might need to create a new Sector instance or handle the error
        sector = Sector.get_sector_by_id(sector_id)
        if not sector:
            return jsonify({'error': 'Sector not found'}), 404

        # Create a UE instance with the provided parameters
        # Assuming the UE class has been adjusted to accept a service_type parameter directly
        ue_config = {
            'ue_id': ue_id,
            'service_type': service_type,
            # Include other necessary parameters for UE initialization here
        }
        ue = UE(config=ue_config, ue_id=ue_id, service_type=service_type)

        # Add the UE to the sector
        with lock:  # Ensure thread safety
            success = sector.add_ue(ue)

        if success:
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
        # Retrieve the sector by its ID
        sector = Sector.get_sector_by_id(sector_id)
        if not sector:
            return jsonify({'error': 'Sector not found'}), 404

        # Remove the UE from the sector
        with lock:  # Ensure thread safety
            success = sector.remove_ue(ue_id)

        if success:
            return jsonify({'message': f'UE {ue_id} removed successfully from sector {sector_id}'}), 200
        else:
            return jsonify({'error': 'Failed to remove UE from sector'}), 500
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)