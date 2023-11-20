#Functions for generating different types of traffic (voice, video, gaming, IoT).
#traffic_generator.py

import random
def generate_voice_traffic():
    # Approx 13 Kbps for VoLTE, let's assume a 20ms interval
    data_size = (13 * 20) / 8 / 1000  # Convert Kbps to KB
    interval = 0.02  # 20 ms
    return data_size, interval

def generate_video_traffic():
    # HD Video streaming at 5 Mbps, assume a 1-second interval
    data_size = (5 * 1024 * 1) / 8  # Convert Mbps to MB
    interval = 1  # 1 second
    return data_size, interval

def generate_gaming_traffic():
    # Online gaming, assuming 50 Kbps, with a 100ms interval
    data_size = (50 * 100) / 8 / 1000  # Convert Kbps to KB
    interval = 0.1  # 100 ms
    return data_size, interval

def generate_iot_traffic():
    # Small IoT data packets, assuming 10 KB every 30 seconds
    data_size = 10  # 10 KB
    interval = 30  # 30 seconds
    return data_size, interval


