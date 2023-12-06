#Functions for generating different types of traffic (voice, video, gaming, IoT).
#traffic_generator.py in traffic folder
import random
import time
class TrafficController:
    def __init__(self):
        # Initialize default traffic parameters
        self.voice_traffic_params = {'bitrate': (8, 16)}
        self.video_traffic_params = {'num_streams': (1, 5), 'stream_bitrate': (3, 8)}
        self.gaming_traffic_params = {'bitrate': (30, 70)}
        self.iot_traffic_params = {'packet_size': (5, 15), 'interval': (10, 60)}
        self.data_traffic_params = {'bitrate': (1, 10), 'interval': (0.5, 2)}

        # Initialize jitter, delay, and packet loss for each traffic type
        self.voice_jitter = 0
        self.voice_delay = 0
        self.voice_packet_loss_rate = 0

        self.video_jitter = 0
        self.video_delay = 0
        self.video_packet_loss_rate = 0

        self.gaming_jitter = 0
        self.gaming_delay = 0
        self.gaming_packet_loss_rate = 0

        self.iot_jitter = 0
        self.iot_delay = 0
        self.iot_packet_loss_rate = 0

        self.data_jitter = 0
        self.data_delay = 0
        self.data_packet_loss_rate = 0
    
    # Update methods for jitter, delay, and packet loss
    def update_voice_traffic_parameters(self, jitter, delay, packet_loss_rate):
        self.voice_jitter = jitter
        self.voice_delay = delay
        self.voice_packet_loss_rate = packet_loss_rate

    def update_video_traffic_parameters(self, jitter, delay, packet_loss_rate):
        self.video_jitter = jitter
        self.video_delay = delay
        self.video_packet_loss_rate = packet_loss_rate

    def update_gaming_traffic_parameters(self, jitter, delay, packet_loss_rate):
        self.gaming_jitter = jitter
        self.gaming_delay = delay
        self.gaming_packet_loss_rate = packet_loss_rate
        
    def update_iot_traffic_parameters(self, jitter, delay, packet_loss_rate):
        self.iot_jitter = jitter
        self.iot_delay = delay
        self.iot_packet_loss_rate = packet_loss_rate
    def update_data_traffic_parameters(self, jitter, delay, packet_loss_rate):
        self.data_jitter = jitter
        self.data_delay = delay
        self.data_packet_loss_rate = packet_loss_rate 

        
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

    # Traffic generation methods with conditional application of jitter, delay, and packet loss
    #jitter, delay, and packet_loss_rate are optional features that are disabled by default. They can be enabled and configured using the set_jitter, set_delay, and set_packet_loss_rate methods. The traffic generation methods have been updated to apply these features conditionally.
    def generate_voice_traffic(self):
        time.sleep(self.voice_delay)  # Use voice-specific delay
        jitter = random.uniform(0, self.voice_jitter) if self.voice_jitter > 0 else 0
        bitrate = random.uniform(*self.voice_traffic_params['bitrate'])
        interval = 0.02
        data_size = (bitrate * interval) / 8 / 1000

        # Apply jitter
        time.sleep(jitter)

        # Simulate packet loss
        if random.random() < self.voice_packet_loss_rate:
            data_size = 0  # Packet is lost

        return data_size, interval

    def generate_video_traffic(self):
        jitter = random.uniform(*self.jitter_range) if self.jitter_range != (0, 0) else 0
        time.sleep(self.delay + jitter)  # Apply jitter to the delay
        num_streams = random.randint(*self.video_traffic_params['num_streams'])
        data_size = 0
        interval = 1
        for _ in range(num_streams):
            stream_bitrate = random.uniform(*self.video_traffic_params['stream_bitrate']) * 1024
            # Simulate packet loss
            if random.random() >= self.packet_loss_rate:
                data_size += (stream_bitrate * interval) / 8
        return data_size, interval

    def generate_gaming_traffic(self):
        jitter = random.uniform(*self.jitter_range) if self.jitter_range != (0, 0) else 0
        time.sleep(self.delay + jitter)  # Apply jitter to the delay
        bitrate = random.uniform(*self.gaming_traffic_params['bitrate'])
        interval = 0.1
        data_size = (bitrate * interval) / 8 / 1000
        # Simulate packet loss
        if random.random() < self.packet_loss_rate:
            data_size = 0  # Packet is lost
        return data_size, interval
    
    def generate_iot_traffic(self):
        jitter = random.uniform(0, self.jitter) if self.jitter > 0 else 0
        time.sleep(self.delay + jitter)  # Apply jitter to the delay
        data_size = random.randint(*self.iot_traffic_params['packet_size'])
        interval = random.uniform(*self.iot_traffic_params['interval'])
    
        # Simulate packet loss
        if random.random() < self.packet_loss_rate:
            data_size = 0  # Packet is lost
    
        return data_size, interval

    def generate_data_traffic(self):
        jitter = random.uniform(0, self.jitter) if self.jitter > 0 else 0
        time.sleep(self.delay + jitter)  # Apply jitter to the delay
        bitrate = random.uniform(*self.data_traffic_params['bitrate']) * 1024
        interval = random.uniform(*self.data_traffic_params['interval'])
        data_size = (bitrate * interval) / 8
    
        # Simulate packet loss
        if random.random() < self.packet_loss_rate:
            data_size = 0  # Packet is lost
    
        return data_size, interval

# Example usage with delay
# Example usage
#traffic_controller = TrafficController()
#traffic_controller.set_jitter(0.1)  # Enable jitter with a maximum of 0.1 seconds
#traffic_controller.set_delay(1)  # Set a fixed delay of 1 second
#traffic_controller.set_packet_loss_rate(0.01)  # Set a packet loss rate of 1%

# Print statements can be uncommented to see the output
# print("Voice Traffic:", voice_data, "KB, Interval:", voice_interval, "seconds")
# print("Video Traffic:", video_data, "MB, Interval:", video_interval, "second")
# print("Gaming Traffic:", gaming_data, "KB, Interval:", gaming_interval, "seconds")
# print("IoT Traffic:", iot_data, "KB, Interval:", iot_interval, "seconds")
# print("Data Traffic:", data_data, "MB, Interval:", data_interval, "seconds")


