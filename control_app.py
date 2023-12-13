# control_app.py in root directory
from flask import Flask, request
from traffic.traffic_generator import TrafficController
from logs.logger_config import setup_logger
from logs.logger_config import traffic_update_logger

app = Flask(__name__)
traffic_controller = TrafficController()

@app.route('/', methods=['GET'])
def index():
    return 'Welcome to the 5G RAN Simulator!', 200

@app.route('/update_voice_traffic', methods=['POST'])
def update_voice_traffic():
    data = request.json
    bitrate_range = data.get('bitrate_range')
    jitter = data.get('jitter')
    delay = data.get('delay')
    packet_loss_rate = data.get('packet_loss_rate')
    traffic_controller.update_voice_traffic(bitrate_range)
    traffic_controller.update_voice_traffic_parameters(jitter, delay, packet_loss_rate)
    traffic_update_logger.info(f'Voice traffic updated: bitrate_range={bitrate_range}, jitter={jitter}, delay={delay}, packet_loss_rate={packet_loss_rate}')
    return {'message': 'Voice traffic parameters updated successfully'}, 200

@app.route('/update_video_traffic', methods=['POST'])
def update_video_traffic():
    data = request.json
    num_streams_range = data.get('num_streams_range')
    stream_bitrate_range = data.get('stream_bitrate_range')
    jitter = data.get('jitter')
    delay = data.get('delay')
    packet_loss_rate = data.get('packet_loss_rate')
    traffic_controller.update_video_traffic(num_streams_range, stream_bitrate_range)
    traffic_controller.update_video_traffic_parameters(jitter, delay, packet_loss_rate)
    traffic_update_logger.info(f'Video traffic updated: num_streams_range={num_streams_range}, stream_bitrate_range={stream_bitrate_range}, jitter={jitter}, delay={delay}, packet_loss_rate={packet_loss_rate}')
    return {'message': 'Video traffic parameters updated successfully'}, 200

@app.route('/update_gaming_traffic', methods=['POST'])
def update_gaming_traffic():
    data = request.json
    bitrate_range = data.get('bitrate_range')
    jitter = data.get('jitter')
    delay = data.get('delay')
    packet_loss_rate = data.get('packet_loss_rate')
    traffic_controller.update_gaming_traffic(bitrate_range)
    traffic_controller.update_gaming_traffic_parameters(jitter, delay, packet_loss_rate)
    traffic_update_logger.info(f'Gaming traffic updated: bitrate_range={bitrate_range}, jitter={jitter}, delay={delay}, packet_loss_rate={packet_loss_rate}')
    return {'message': 'Gaming traffic parameters updated successfully'}, 200

@app.route('/update_iot_traffic', methods=['POST'])
def update_iot_traffic():
    data = request.json
    packet_size_range = data.get('packet_size_range')
    interval_range = data.get('interval_range')
    jitter = data.get('jitter')
    delay = data.get('delay')
    packet_loss_rate = data.get('packet_loss_rate')
    traffic_controller.update_iot_traffic(packet_size_range, interval_range)
    traffic_controller.update_iot_traffic_parameters(jitter, delay, packet_loss_rate)
    traffic_update_logger.info(f'IoT traffic updated: packet_size_range={packet_size_range}, interval_range={interval_range}, jitter={jitter}, delay={delay}, packet_loss_rate={packet_loss_rate}')
    return {'message': 'IoT traffic parameters updated successfully'}, 200

@app.route('/update_data_traffic', methods=['POST'])
def update_data_traffic():
    data = request.json
    bitrate_range = data.get('bitrate_range')
    interval_range = data.get('interval_range')
    jitter = data.get('jitter')
    delay = data.get('delay')
    packet_loss_rate = data.get('packet_loss_rate')
    traffic_controller.update_data_traffic(bitrate_range, interval_range)
    traffic_controller.update_data_traffic_parameters(jitter, delay, packet_loss_rate)
    traffic_update_logger.info(f'Data traffic updated: bitrate_range={bitrate_range}, interval_range={interval_range}, jitter={jitter}, delay={delay}, packet_loss_rate={packet_loss_rate}')
    return {'message': 'Data traffic parameters updated successfully'}, 200

if __name__ == '__main__':
    app.run(debug=True)