from flask import Flask, request, jsonify
from network.ue import UE
from network.sector import Sector
from threading import Lock
import traceback
import threading

app = Flask(__name__)
lock = threading.Lock()

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

@app.route('/update_ue', methods=['POST'])
def update_ue():
    data = request.json
    ue_id = data['ue_id']
    try:
        # Retrieve the UE instance by its ID
        # This assumes you have a method to get a UE instance by ID. If not, you'll need to implement it.
        ue = get_ue_instance_by_id(ue_id)
        if not ue:
            return jsonify({'error': 'UE not found'}), 404

        # Update the UE parameters
        # This is a simplified example. You'll need to implement the logic to update the parameters based on the request.
        for param, value in data.items():
            if hasattr(ue, param) and param != 'ue_id':  # Prevent changing the UE ID
                setattr(ue, param, value)

        return jsonify({'message': f'UE {ue_id} updated successfully'}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500