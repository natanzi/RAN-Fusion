# control_app.py in root directory
from flask_cors import CORS, cross_origin
from flask import Flask, request, jsonify
from traffic.traffic_generator import TrafficController
from logs.logger_config import setup_logger
from logs.logger_config import traffic_update,server_logger 
from multiprocessing import Queue
import traceback
from datetime import datetime

# Global flag to indicate if an update has been received
update_received = False

# Create Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # This line allows all domains

# Assuming command_queue is made accessible here, for example, as a global variable
command_queue = Queue()

# Ensure TrafficController instance is accessible here, possibly as a global or through an application context
global traffic_controller
traffic_controller = TrafficController(command_queue)

def validate_traffic_parameters(params, param_types):
    missing_params = [param for param, param_type in param_types.items() if param not in params or not isinstance(params[param], param_type)]
    if missing_params:
        return False, f"Missing or invalid parameters: {', '.join(missing_params)}"
    return True, ""

@app.route('/', methods=['GET'])
def index():
    return 'Welcome to the 5G RAN Simulator!', 200
############################################################################################################
@app.route('/update_voice_traffic', methods=['POST'])
def update_voice_traffic():
    global update_received
    data = request.json
    print("Received data for voice traffic update:", data)  # Print received data to the terminal

    expected_types = {
        'bitrate_range': list,
        'jitter': (int, float),
        'delay': (int, float),
        'packet_loss_rate': (int, float)
    }
    is_valid, message = validate_traffic_parameters(data, expected_types)
    if not is_valid:
        print("Validation failed for voice traffic update:", message)  # Print validation failure to the terminal
        return {'error': message}, 400

    try:
        success = traffic_controller.update_voice_traffic(data['bitrate_range'])
        if success:
            update_id = datetime.now().timestamp()  # Unique identifier for the update
            command = {
                'type': 'update',
                'service_type': 'voice',
                'data': data,
                'update_id': update_id  # Include the unique identifier in the command
            }
            command_queue.put(command)  # Send the structured command to the command queue
            traffic_update.info(f"Voice traffic update command sent: {command}")
            print(f"Voice traffic update command sent with ID: {update_id}")  # Print success message to the terminal
            return {'message': 'Voice traffic update command sent', 'acknowledged': True, 'update_id': update_id}, 200
        else:
            print("Failed to apply voice traffic update.")  # Print failure message to the terminal
            return {'error': 'Failed to update parameters', 'acknowledged': False}, 500
    except Exception as e:
        traffic_update.error(f'Failed to update voice traffic: {e}')
        print("Exception occurred during voice traffic update:", e)  # Print exception message to the terminal
        print(traceback.format_exc())  # Print stack trace to the terminal
        return {'error': str(e), 'acknowledged': False}, 500
#############################################################################################################
@app.route('/update_video_traffic', methods=['POST'])
def update_video_traffic():
    global update_received
    data = request.json
    print("Received data for video traffic update:", data)  # Print received data to the terminal

    expected_types = {
        'num_streams_range': list,
        'stream_bitrate_range': list,
        'jitter': (int, float),
        'delay': (int, float),
        'packet_loss_rate': (int, float)
    }
    is_valid, message = validate_traffic_parameters(data, expected_types)
    if not is_valid:
        print("Validation failed for video traffic update:", message)  # Print validation failure to the terminal
        return {'error': message}, 400

    try:
        success = traffic_controller.update_video_traffic(data['num_streams_range'], data['stream_bitrate_range'])
        if success:
            update_id = datetime.now().timestamp()  # Unique identifier for the update
            command = {
                'type': 'update',
                'service_type': 'video',
                'data': data,
                'update_id': update_id  # Include the unique identifier in the command
            }
            command_queue.put(command)  # Send the structured command to the command queue
            traffic_update.info(f"Video traffic update command sent: {command}")
            print(f"Video traffic update command sent with ID: {update_id}")  # Print success message to the terminal
            return {'message': 'Video traffic update command sent', 'acknowledged': True, 'update_id': update_id}, 200
        else:
            print("Failed to apply video traffic update.")  # Print failure message to the terminal
            return {'error': 'Failed to update parameters', 'acknowledged': False}, 500
    except Exception as e:
        traffic_update.error(f'Failed to update video traffic: {e}')
        print("Exception occurred during video traffic update:", e)  # Print exception message to the terminal
        print(traceback.format_exc())  # Print stack trace to the terminal
        return {'error': str(e), 'acknowledged': False}, 500
######################################################################################################
@app.route('/update_gaming_traffic', methods=['POST'])
def update_gaming_traffic():
    app.logger.info('Processing request for /update_gaming_traffic')
    data = request.json
    print("Received data:", data)  # This will print the received data to the terminal

    expected_types = {
        'bitrate_range': list,
        'jitter': (int, float),
        'delay': (int, float),
        'packet_loss_rate': (int, float)
    }
    is_valid, message = validate_traffic_parameters(data, expected_types)
    if not is_valid:
        print("Validation failed:", message)  # This will print the validation failure message to the terminal
        return {'error': message}, 400

    try:
        success = traffic_controller.update_gaming_traffic(data['bitrate_range'])
        if success:
            update_id = datetime.now().timestamp()  # Unique identifier for the update
            command = {
                'type': 'update',
                'service_type': 'gaming',
                'data': data,
                'update_id': update_id  # Include the unique identifier in the command
            }
            command_queue.put(command)  # Send the structured command to the command queue
            traffic_update.info(f"Gaming traffic update command sent: {command}")
            print(f"Gaming traffic update command sent with ID: {update_id}")  # This will print the success message to the terminal
            return {'message': 'Gaming traffic update command sent', 'acknowledged': True, 'update_id': update_id}, 200
        else:
            print("Failed to apply gaming traffic update.")  # This will print the failure message to the terminal
            return {'error': 'Failed to update parameters', 'acknowledged': False}, 500
    except Exception as e:
        traffic_update.error(f'Failed to update gaming traffic: {e}')
        print("Exception occurred:", e)  # This will print the exception message to the terminal
        print(traceback.format_exc())  # This will print the stack trace to the terminal
        return {'error': str(e), 'acknowledged': False}, 500
###########################################################################################################################
@app.route('/update_iot_traffic', methods=['POST'])
def update_iot_traffic():
    data = request.json
    print("Received data for IoT traffic update:", data)  # Print received data to the terminal

    expected_types = {
        'packet_size_range': list,
        'interval_range': list,
        'jitter': (int, float),
        'delay': (int, float),
        'packet_loss_rate': (int, float)
    }
    is_valid, message = validate_traffic_parameters(data, expected_types)
    if not is_valid:
        print("Validation failed for IoT traffic update:", message)  # Print validation failure to the terminal
        return {'error': message}, 400

    try:
        success = traffic_controller.update_iot_traffic(data['packet_size_range'], data['interval_range'])
        if success:
            update_id = datetime.now().timestamp()  # Unique identifier for the update
            command = {
                'type': 'update',
                'service_type': 'iot',
                'data': data,
                'update_id': update_id  # Include the unique identifier in the command
            }
            command_queue.put(command)  # Send the structured command to the command queue
            traffic_update.info(f"IoT traffic update command sent: {command}")
            print(f"IoT traffic update command sent with ID: {update_id}")  # Print success message to the terminal
            return {'message': 'IoT traffic update command sent', 'acknowledged': True, 'update_id': update_id}, 200
        else:
            print("Failed to apply IoT traffic update.")  # Print failure message to the terminal
            return {'error': 'Failed to update parameters', 'acknowledged': False}, 500
    except Exception as e:
        traffic_update.error(f'Failed to update IoT traffic: {e}')
        print("Exception occurred during IoT traffic update:", e)  # Print exception message to the terminal
        print(traceback.format_exc())  # Print stack trace to the terminal
        return {'error': str(e), 'acknowledged': False}, 500
###########################################################################################################################
@app.route('/update_data_traffic', methods=['POST'])
def update_data_traffic():
    data = request.json
    print("Received data for data traffic update:", data)  # Print received data to the terminal

    expected_types = {
        'bitrate_range': list,
        'interval_range': list,
        'jitter': (int, float),
        'delay': (int, float),
        'packet_loss_rate': (int, float)
    }
    is_valid, message = validate_traffic_parameters(data, expected_types)
    if not is_valid:
        print("Validation failed for data traffic update:", message)  # Print validation failure to the terminal
        return {'error': message}, 400

    try:
        success = traffic_controller.update_data_traffic(data['bitrate_range'], data['interval_range'])
        if success:
            update_id = datetime.now().timestamp()  # Unique identifier for the update
            command = {
                'type': 'update',
                'service_type': 'data',
                'data': data,
                'update_id': update_id  # Include the unique identifier in the command
            }
            command_queue.put(command)  # Send the structured command to the command queue
            traffic_update.info(f"Data traffic update command sent: {command}")
            print(f"Data traffic update command sent with ID: {update_id}")  # Print success message to the terminal
            return {'message': 'Data traffic update command sent', 'acknowledged': True, 'update_id': update_id}, 200
        else:
            print("Failed to apply data traffic update.")  # Print failure message to the terminal
            return {'error': 'Failed to update parameters', 'acknowledged': False}, 500
    except Exception as e:
        traffic_update.error(f'Failed to update data traffic: {e}')
        print("Exception occurred during data traffic update:", e)  # Print exception message to the terminal
        print(traceback.format_exc())  # Print stack trace to the terminal
        return {'error': str(e), 'acknowledged': False}, 500
###########################################################################################################################
@app.route('/check_update_status', methods=['GET'])
def check_update_status():
    update_id = request.args.get('update_id')
    if update_id and update_id in traffic_controller.update_statuses:
        status = traffic_controller.update_statuses[update_id]
        return jsonify({'update_id': update_id, 'status': status}), 200
    else:
        return jsonify({'error': 'Invalid or unknown update ID'}), 404
###########################################################################################################################

@app.route('/test', methods=['GET'])
def test_endpoint():
    return jsonify({'message': 'CORS Test successful'}), 200    

if __name__ == '__main__':
    app.run(debug=True)
