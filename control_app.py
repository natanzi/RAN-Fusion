# control_app.py in root directory
from flask_cors import CORS
from flask import Flask, request
from traffic.traffic_generator import TrafficController
from logs.logger_config import setup_logger
from logs.logger_config import traffic_update
from multiprocessing import Queue

# Assuming command_queue is made accessible here, for example, as a global variable
command_queue = Queue()

# Ensure TrafficController instance is accessible here, possibly as a global or through an application context
global traffic_controller

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
traffic_controller = TrafficController()

def validate_traffic_parameters(params, param_types):
    for param, param_type in param_types.items():
        if param not in params or not isinstance(params[param], param_type):
            return False, f"Invalid or missing parameter: {param}"
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
        traffic_controller.update_voice_traffic(data['bitrate_range'])
        traffic_controller.update_voice_traffic_parameters(data['jitter'], data['delay'], data['packet_loss_rate'])
        traffic_update.info(f"Voice traffic updated: {data}")
        return {'message': 'Voice traffic parameters updated successfully'}, 200
    except Exception as e:
        traffic_update.error(f'Failed to update voice traffic: {e}')
        # Send a command to restart the traffic generation process
        command_queue.put('restart')
        return {'error': str(e)}, 500

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
        traffic_controller.update_video_traffic(data['num_streams_range'], data['stream_bitrate_range'])
        traffic_controller.update_video_traffic_parameters(data['jitter'], data['delay'], data['packet_loss_rate'])
        traffic_update.info(f"Video traffic updated: {data}")
        return {'message': 'Video traffic parameters updated successfully'}, 200
    except Exception as e:
        traffic_update.error(f'Failed to update video traffic: {e}')
        # Send a command to restart the traffic generation process
        command_queue.put('restart')
        return {'error': str(e)}, 500

@app.route('/update_gaming_traffic', methods=['POST'])
def update_gaming_traffic():
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
        traffic_controller.update_gaming_traffic(data['bitrate_range'])
        traffic_controller.update_gaming_traffic_parameters(data['jitter'], data['delay'], data['packet_loss_rate'])
        traffic_update.info(f"Gaming traffic updated: {data}")
        return {'message': 'Gaming traffic parameters updated successfully'}, 200
    except Exception as e:
        traffic_update.error(f'Failed to update gaming traffic: {e}')
        # Send a command to restart the traffic generation process
        command_queue.put('restart')
        return {'error': str(e)}, 500

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
        traffic_controller.update_iot_traffic(data['packet_size_range'], data['interval_range'])
        traffic_controller.update_iot_traffic_parameters(data['jitter'], data['delay'], data['packet_loss_rate'])
        traffic_update.info(f"IoT traffic updated: {data}")
        return {'message': 'IoT traffic parameters updated successfully'}, 200
    except Exception as e:
        traffic_update.error(f'Failed to update IoT traffic: {e}')
        # Send a command to restart the traffic generation process
        command_queue.put('restart')
        return {'error': str(e)}, 500

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
        traffic_controller.update_data_traffic(data['bitrate_range'], data['interval_range'])
        traffic_controller.update_data_traffic_parameters(data['jitter'], data['delay'], data['packet_loss_rate'])
        traffic_update.info(f"Data traffic updated: {data}")
        return {'message': 'Data traffic parameters updated successfully'}, 200
    except Exception as e:
        traffic_update.error(f'Failed to update data traffic: {e}')
        # Send a command to restart the traffic generation process
        command_queue.put('restart')
        return {'error': str(e)}, 500

if __name__ == '__main__':
    app.run(debug=True)