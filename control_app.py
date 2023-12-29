# control_app.py in root directory
from flask_cors import CORS, cross_origin
from flask import Flask, request, jsonify
from traffic.traffic_generator import TrafficController
from logs.logger_config import setup_logger
from logs.logger_config import traffic_update,server_logger 
from multiprocessing import Queue
import traceback


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

@app.route('/update_voice_traffic', methods=['POST'])
def update_voice_traffic():
    data = request.json
    expected_types = {
        'bitrate_range': list,
        'jitter': (int, float),
        'delay': (int, float),
        'packet_loss_rate': (int, float)
    }
    is_valid, message = validate_traffic_parameters(data, expected_types)
    if not is_valid:
        return {'error': message}, 400

    try:
        success = traffic_controller.update_voice_traffic(data['bitrate_range'])
        if success:
            # Send a command to restart the traffic generation process
            command_queue.put('restart')
            return {'message': 'Voice traffic parameters updated successfully', 'acknowledged': True}, 200
        else:
            return {'error': 'Failed to update parameters', 'acknowledged': False}, 500
    except Exception as e:
        traffic_update.error(f'Failed to update voice traffic: {e}')
        return {'error': str(e), 'acknowledged': False}, 500

@app.route('/update_video_traffic', methods=['POST'])
def update_video_traffic():
    data = request.json
    expected_types = {
        'num_streams_range': list,
        'stream_bitrate_range': list,
        'jitter': (int, float),
        'delay': (int, float),
        'packet_loss_rate': (int, float)
    }
    is_valid, message = validate_traffic_parameters(data, expected_types)
    if not is_valid:
        return {'error': message}, 400

    try:
        success = traffic_controller.update_video_traffic(data['num_streams_range'], data['stream_bitrate_range'])
        if success:
            traffic_controller.update_video_traffic_parameters(data['jitter'], data['delay'], data['packet_loss_rate'])
            traffic_update.info(f"Video traffic updated: {data}")
            # Send a command to restart the traffic generation process
            command_queue.put('restart')
            return {'message': 'Video traffic parameters updated successfully', 'acknowledged': True}, 200
        else:
            return {'error': 'Failed to update parameters', 'acknowledged': False}, 500
    except Exception as e:
        traffic_update.error(f'Failed to update video traffic: {e}')
        return {'error': str(e), 'acknowledged': False}, 500

@app.route('/update_gaming_traffic', methods=['POST'])
def update_gaming_traffic():
    app.logger.info('Processing request for /some_endpoint')
    print("Received data:", request.json)
    data = request.json
    expected_types = {
        'bitrate_range': list,
        'jitter': (int, float),
        'delay': (int, float),
        'packet_loss_rate': (int, float)
    }
    is_valid, message = validate_traffic_parameters(data, expected_types)
    if not is_valid:
        print("Validation failed:", message) 
        return {'error': message}, 400

    try:
        success = traffic_controller.update_gaming_traffic(data['bitrate_range'])
        if success:
            traffic_controller.update_gaming_traffic_parameters(data['jitter'], data['delay'], data['packet_loss_rate'])
            traffic_update.info(f"Gaming traffic updated: {data}")
            # Send a command to restart the traffic generation process
            command_queue.put('restart')
            return {'message': 'Gaming traffic parameters updated successfully', 'acknowledged': True}, 200
        else:
            return {'error': 'Failed to update parameters', 'acknowledged': False}, 500
    except Exception as e:
        traffic_update.error(f'Failed to update gaming traffic: {e}')
        print("Exception:", e)
        print(traceback.format_exc())
        return {'error': str(e), 'acknowledged': False}, 500

@app.route('/update_iot_traffic', methods=['POST'])
def update_iot_traffic():
    data = request.json
    expected_types = {
        'packet_size_range': list,
        'interval_range': list,
        'jitter': (int, float),
        'delay': (int, float),
        'packet_loss_rate': (int, float)
    }
    is_valid, message = validate_traffic_parameters(data, expected_types)
    if not is_valid:
        return {'error': message}, 400

    try:
        success = traffic_controller.update_iot_traffic(data['packet_size_range'], data['interval_range'])
        if success:
            traffic_controller.update_iot_traffic_parameters(data['jitter'], data['delay'], data['packet_loss_rate'])
            traffic_update.info(f"IoT traffic updated: {data}")
            # Send a command to restart the traffic generation process
            command_queue.put('restart')
            return {'message': 'IoT traffic parameters updated successfully', 'acknowledged': True}, 200
        else:
            return {'error': 'Failed to update parameters', 'acknowledged': False}, 500
    except Exception as e:
        traffic_update.error(f'Failed to update IoT traffic: {e}')
        return {'error': str(e), 'acknowledged': False}, 500

@app.route('/update_data_traffic', methods=['POST'])
def update_data_traffic():
    data = request.json
    expected_types = {
        'bitrate_range': list,
        'interval_range': list,
        'jitter': (int, float),
        'delay': (int, float),
        'packet_loss_rate': (int, float)
    }
    is_valid, message = validate_traffic_parameters(data, expected_types)
    if not is_valid:
        return {'error': message}, 400

    try:
        success = traffic_controller.update_data_traffic(data['bitrate_range'], data['interval_range'])
        if success:
            traffic_controller.update_data_traffic_parameters(data['jitter'], data['delay'], data['packet_loss_rate'])
            traffic_update.info(f"Data traffic updated: {data}")
            # Send a command to restart the traffic generation process
            command_queue.put('restart')
            return {'message': 'Data traffic parameters updated successfully', 'acknowledged': True}, 200
        else:
            return {'error': 'Failed to update parameters', 'acknowledged': False}, 500
    except Exception as e:
        traffic_update.error(f'Failed to update data traffic: {e}')
        return {'error': str(e), 'acknowledged': False}, 500

@app.route('/test', methods=['GET'])
def test_endpoint():
    return jsonify({'message': 'CORS Test successful'}), 200    

if __name__ == '__main__':
    app.run(debug=True)
