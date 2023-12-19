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
    def generate_voice_traffic(self):
        time.sleep(self.voice_delay)  # Use voice-specific delay
        jitter = random.uniform(0, self.voice_jitter) if self.voice_jitter > 0 else 0
        bitrate = random.uniform(*self.voice_traffic_params['bitrate'])
        interval = 0.02 # Interval duration in seconds
        data_size = (bitrate * interval) / 8 / 1000  #MB

        # Apply jitter
        time.sleep(jitter)

        # Simulate packet loss
        if random.random() < self.voice_packet_loss_rate:
            data_size = 0  # Packet is lost

        return data_size, interval, bitrate, jitter

    def generate_video_traffic(self):
        time.sleep(self.video_delay)  # Use video-specific delay
        jitter = random.uniform(0, self.video_jitter) if self.video_jitter > 0 else 0
        num_streams = random.randint(*self.video_traffic_params['num_streams'])
        data_size = 0
        interval = 1 # Interval duration in seconds
        for _ in range(num_streams):
            stream_bitrate = random.uniform(*self.video_traffic_params['stream_bitrate']) * 1024
        # Apply jitter
            time.sleep(jitter)
        # Simulate packet loss
            if random.random() < self.video_packet_loss_rate:
                continue  # Skip this stream due to packet loss
            data_size += (stream_bitrate * interval) / 8
        return data_size, interval, self.video_delay, jitter, self.video_packet_loss_rate

    def generate_gaming_traffic(self):
        time.sleep(self.gaming_delay)  # Use gaming-specific delay
        jitter = random.uniform(0, self.gaming_jitter) if self.gaming_jitter > 0 else 0
        bitrate = random.uniform(*self.gaming_traffic_params['bitrate'])
        interval = 0.1 # Interval duration in seconds
        data_size = (bitrate * interval) / 8 / 1000
        # Apply jitter
        time.sleep(jitter)
        # Simulate packet loss
        if random.random() < self.gaming_packet_loss_rate:
            data_size = 0  # Packet is lost
        return data_size, interval, self.video_delay, jitter, self.video_packet_loss_rate
    
    def generate_iot_traffic(self):
        time.sleep(self.iot_delay)  # Use IoT-specific delay
        jitter = random.uniform(0, self.iot_jitter) if self.iot_jitter > 0 else 0
        data_size = random.randint(*self.iot_traffic_params['packet_size'])
        interval = random.uniform(*self.iot_traffic_params['interval'])
        # Apply jitter
        time.sleep(jitter)
        # Simulate packet loss
        if random.random() < self.iot_packet_loss_rate:
            data_size = 0  # Packet is lost
        return data_size, interval, self.iot_delay, jitter, self.iot_packet_loss_rate

    def generate_data_traffic(self):
        time.sleep(self.data_delay)  # Use data-specific delay
        jitter = random.uniform(0, self.data_jitter) if self.data_jitter > 0 else 0
        bitrate = random.uniform(*self.data_traffic_params['bitrate']) * 1024
        interval = random.uniform(*self.data_traffic_params['interval'])
        data_size = (bitrate * interval) / 8
        # Apply jitter
        time.sleep(jitter)
        # Simulate packet loss
        if random.random() < self.data_packet_loss_rate:
            data_size = 0  # Packet is lost
        return data_size, interval, self.data_delay, jitter, self.data_packet_loss_rate

# Example usage
#traffic_controller = TrafficController()

# Update traffic parameters as needed, for example:
#traffic_controller.update_voice_traffic_parameters(jitter=0.1, delay=1, packet_loss_rate=0.01)
#traffic_controller.update_video_traffic_parameters(jitter=0.1, delay=1, packet_loss_rate=0.01)
# ... and so on for other traffic types

# Generate traffic and print the results
#voice_data, voice_interval = traffic_controller.generate_voice_traffic()
#video_data, video_interval = traffic_controller.generate_video_traffic()
#gaming_data, gaming_interval = traffic_controller.generate_gaming_traffic()
#iot_data, iot_interval = traffic_controller.generate_iot_traffic()
#data_data, data_interval = traffic_controller.generate_data_traffic()

# Print statements to see the output
#print("Voice Traffic:", voice_data, "KB, Interval:", voice_interval, "seconds")
#print("Video Traffic:", video_data, "MB, Interval:", video_interval, "second")
#print("Gaming Traffic:", gaming_data, "KB, Interval:", gaming_interval, "seconds")
#print("IoT Traffic:", iot_data, "KB, Interval:", iot_interval, "seconds")
#print("Data Traffic:", data_data, "MB, Interval:", data_interval, "seconds")


