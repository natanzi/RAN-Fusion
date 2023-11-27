#Functions for generating different types of traffic (voice, video, gaming, IoT).
#traffic_generator.py in traffic folder
import random

class TrafficController:
    def __init__(self):
        # Initialize default traffic parameters
        self.voice_traffic_params = {'bitrate': (8, 16)}
        self.video_traffic_params = {'num_streams': (1, 5), 'stream_bitrate': (3, 8)}
        self.gaming_traffic_params = {'bitrate': (30, 70)}
        self.iot_traffic_params = {'packet_size': (5, 15), 'interval': (10, 60)}
        self.data_traffic_params = {'bitrate': (1, 10), 'interval': (0.5, 2)}

    def update_voice_traffic(self, bitrate_range):
        self.voice_traffic_params['bitrate'] = bitrate_range

    def update_video_traffic(self, num_streams_range, stream_bitrate_range):
        self.video_traffic_params['num_streams'] = num_streams_range
        self.video_traffic_params['stream_bitrate'] = stream_bitrate_range

    def update_gaming_traffic(self, bitrate_range):
        self.gaming_traffic_params['bitrate'] = bitrate_range

    def update_iot_traffic(self, packet_size_range, interval_range):
        self.iot_traffic_params['packet_size'] = packet_size_range
        self.iot_traffic_params['interval'] = interval_range

    def update_data_traffic(self, bitrate_range, interval_range):
        self.data_traffic_params['bitrate'] = bitrate_range
        self.data_traffic_params['interval'] = interval_range    

    def generate_voice_traffic(self):
        bitrate = random.uniform(*self.voice_traffic_params['bitrate'])
        interval = 0.02
        data_size = (bitrate * interval) / 8 / 1000
        return data_size, interval

    def generate_video_traffic(self):
        num_streams = random.randint(*self.video_traffic_params['num_streams'])
        data_size = 0
        interval = 1
        for _ in range(num_streams):
            stream_bitrate = random.uniform(*self.video_traffic_params['stream_bitrate']) * 1024
            data_size += (stream_bitrate * interval) / 8
        return data_size, interval

    def generate_gaming_traffic(self):
        bitrate = random.uniform(*self.gaming_traffic_params['bitrate'])
        interval = 0.1
        data_size = (bitrate * interval) / 8 / 1000
        return data_size, interval

    def generate_iot_traffic(self):
        data_size = random.randint(*self.iot_traffic_params['packet_size'])
        interval = random.uniform(*self.iot_traffic_params['interval'])
        return data_size, interval

    def generate_data_traffic(self):
        bitrate = random.uniform(*self.data_traffic_params['bitrate']) * 1024
        interval = random.uniform(*self.data_traffic_params['interval'])
        data_size = (bitrate * interval) / 8
        return data_size, interval

# Example usage
traffic_controller = TrafficController()
voice_data, voice_interval = traffic_controller.generate_voice_traffic()
video_data, video_interval = traffic_controller.generate_video_traffic()
gaming_data, gaming_interval = traffic_controller.generate_gaming_traffic()
iot_data, iot_interval = traffic_controller.generate_iot_traffic()
data_data, data_interval = traffic_controller.generate_data_traffic()

#print("Voice Traffic:", voice_data, "KB, Interval:", voice_interval, "seconds")
#print("Video Traffic:", video_data, "MB, Interval:", video_interval, "second")
#print("Gaming Traffic:", gaming_data, "KB, Interval:", gaming_interval, "seconds")
#print("IoT Traffic:", iot_data, "KB, Interval:", iot_interval, "seconds")
#print("Data Traffic:", data_data, "MB, Interval:", data_interval, "seconds")


