#Functions for generating different types of traffic (voice, video, gaming, IoT).
#traffic_generator.py

import random

def generate_voice_traffic():
    # Voice traffic with variable data rate between 8-16 Kbps
    bitrate = random.uniform(8, 16)  # Random bitrate within range
    interval = 0.02  # 20 ms interval
    data_size = (bitrate * interval) / 8 / 1000  # Convert Kbps to KB
    return data_size, interval

def generate_video_traffic():
    # Video traffic with multiple streams
    num_streams = random.randint(1, 5)  # Random number of streams
    data_size = 0
    interval = 1  # 1 second
    for _ in range(num_streams):
        stream_bitrate = random.uniform(3, 8) * 1024  # Random bitrate between 3-8 Mbps
        data_size += (stream_bitrate * interval) / 8  # Convert Mbps to MB and sum
    return data_size, interval

def generate_gaming_traffic():
    # Online gaming traffic with varying data rate
    bitrate = random.uniform(30, 70)  # Random bitrate within range
    interval = 0.1  # 100 ms interval
    data_size = (bitrate * interval) / 8 / 1000  # Convert Kbps to KB
    return data_size, interval

def generate_iot_traffic():
    # IoT traffic with variable packet size and interval
    data_size = random.randint(5, 15)  # Random packet size between 5-15 KB
    interval = random.uniform(10, 60)  # Random interval between 10-60 seconds
    return data_size, interval

def generate_data_traffic():
    # Data traffic for downloads or FTP
    bitrate = random.uniform(1, 10) * 1024  # Random bitrate in Mbps
    interval = random.uniform(0.5, 2)  # Interval between 0.5 to 2 seconds
    data_size = (bitrate * interval) / 8  # Convert Mbps to MB
    return data_size, interval

# Example usage
voice_data, voice_interval = generate_voice_traffic()
video_data, video_interval = generate_video_traffic()
gaming_data, gaming_interval = generate_gaming_traffic()
iot_data, iot_interval = generate_iot_traffic()
data_data, data_interval = generate_data_traffic()

print("Voice Traffic:", voice_data, "KB, Interval:", voice_interval, "seconds")
print("Video Traffic:", video_data, "MB, Interval:", video_interval, "second")
print("Gaming Traffic:", gaming_data, "KB, Interval:", gaming_interval, "seconds")
print("IoT Traffic:", iot_data, "KB, Interval:", iot_interval, "seconds")
print("Data Traffic:", data_data, "MB, Interval:", data_interval, "seconds")


