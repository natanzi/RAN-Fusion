# control_app.py in root directory
from flask import Flask, request
from traffic.traffic_generator import TrafficController

app = Flask(__name__)
traffic_controller = TrafficController()

@app.route('/update_voice_traffic', methods=['POST'])
def update_voice_traffic():
    data = request.json
    bitrate_range = data.get('bitrate_range')
    traffic_controller.update_voice_traffic(bitrate_range)
    return {'message': 'Voice traffic updated successfully'}, 200

@app.route('/update_video_traffic', methods=['POST'])
def update_video_traffic():
    data = request.json
    num_streams_range = data.get('num_streams_range')
    stream_bitrate_range = data.get('stream_bitrate_range')
    traffic_controller.update_video_traffic(num_streams_range, stream_bitrate_range)
    return {'message': 'Video traffic updated successfully'}, 200

@app.route('/update_gaming_traffic', methods=['POST'])
def update_gaming_traffic():
    data = request.json
    bitrate_range = data.get('bitrate_range')
    traffic_controller.update_gaming_traffic(bitrate_range)
    return {'message': 'Gaming traffic updated successfully'}, 200

@app.route('/update_iot_traffic', methods=['POST'])
def update_iot_traffic():
    data = request.json
    packet_size_range = data.get('packet_size_range')
    interval_range = data.get('interval_range')
    traffic_controller.update_iot_traffic(packet_size_range, interval_range)
    return {'message': 'IoT traffic updated successfully'}, 200

@app.route('/update_data_traffic', methods=['POST'])
def update_data_traffic():
    data = request.json
    bitrate_range = data.get('bitrate_range')
    interval_range = data.get('interval_range')
    traffic_controller.update_data_traffic(bitrate_range, interval_range)
    return {'message': 'Data traffic updated successfully'}, 200

if __name__ == '__main__':
    app.run(debug=True)