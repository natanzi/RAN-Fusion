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

# ... Create endpoints for updating other traffic types

if __name__ == '__main__':
    app.run(debug=True)