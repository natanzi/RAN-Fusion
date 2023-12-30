# Functions for generating different types of traffic (voice, video, gaming, IoT).
# traffic_generator.py in traffic folder
import random
import time
from logs.logger_config import cell_load_logger, cell_logger, gnodeb_logger, ue_logger, traffic_update 
from threading import Lock
from multiprocessing import Queue
from network.network_state import NetworkState
from threading import Thread
import datetime

class TrafficController:

    def __init__(self, command_queue):
        self.lock = Lock()
        self.command_queue = command_queue
        # Initialize default traffic parameters
        self.voice_traffic_params = {'bitrate': (8, 16)}  # in Kbps
        self.video_traffic_params = {'num_streams': (1, 5), 'stream_bitrate': (3, 8)}  # in Mbps
        self.gaming_traffic_params = {'bitrate': (30, 70)}  # in Kbps
        self.iot_traffic_params = {'packet_size': (5, 15), 'interval': (10, 60)}  # packet size in KB, interval in seconds
        self.data_traffic_params = {'bitrate': (1, 10), 'interval': (0.5, 2)}  # in Mbps
        self.updated_parameters = {}  # Add this to store updated parameters
        self.is_updated = False       # Add this flag to track updates

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
    
    def get_updated_ues(self, network_state):
        from network.ue import UE
        # Assuming network_state.ues is a dictionary with UE IDs as keys
        for ue_id, ue in network_state.ues.items():
            # Update the UE's traffic parameters based on its service type
            if ue.ServiceType.lower() == 'voice':
                ue.update_traffic_model({
                    'data_size': self.voice_traffic_params['data_size'],
                    'interval': self.voice_traffic_params['interval'],
                    'delay': self.voice_delay,
                    'jitter': self.voice_jitter,
                    'packet_loss_rate': self.voice_packet_loss_rate
                })
                traffic_update.info(f"UE {ue_id} updated with new voice traffic parameters.")
            elif ue.ServiceType.lower() == 'video':
                ue.update_traffic_model({
                    'data_size': self.video_traffic_params['data_size'],
                    'interval': self.video_traffic_params['interval'],
                    'delay': self.video_delay,
                    'jitter': self.video_jitter,
                    'packet_loss_rate': self.video_packet_loss_rate
                })
                traffic_update.info(f"UE {ue_id} updated with new video traffic parameters.")
            elif ue.ServiceType.lower() == 'game':
                ue.update_traffic_model({
                    'data_size': self.gaming_traffic_params['data_size'],
                    'interval': self.gaming_traffic_params['interval'],
                    'delay': self.gaming_delay,
                    'jitter': self.gaming_jitter,
                    'packet_loss_rate': self.gaming_packet_loss_rate
                })
                traffic_update.info(f"UE {ue_id} updated with new gaming traffic parameters.")
            elif ue.ServiceType.lower() == 'iot':
                ue.update_traffic_model({
                    'data_size': self.iot_traffic_params['data_size'],
                    'interval': self.iot_traffic_params['interval'],
                    'delay': self.iot_delay,
                    'jitter': self.iot_jitter,
                    'packet_loss_rate': self.iot_packet_loss_rate
                })
                traffic_update.info(f"UE {ue_id} updated with new IoT traffic parameters.")
            elif ue.ServiceType.lower() == 'data':
                ue.update_traffic_model({
                    'data_size': self.data_traffic_params['data_size'],
                    'interval': self.data_traffic_params['interval'],
                    'delay': self.data_delay,
                    'jitter': self.data_jitter,
                    'packet_loss_rate': self.data_packet_loss_rate
                })
                traffic_update.info(f"UE {ue_id} updated with new data traffic parameters.")
            else:
                raise ValueError(f"Unknown service type: {ue.ServiceType}")
        
        # Return the updated UEs
        return list(network_state.ues.values())
    
    def restart_traffic_generation(self):
        with self.lock:
            # Stop the current traffic generation
            self.stop_traffic_generation()
            # Start traffic generation with new parameters
            self.start_traffic_generation()
            # Put a 'restart' command in the queue
            self.command_queue.put('restart')
            traffic_update.info("Traffic generation restarted with new parameters.")
    
    def stop_traffic_generation(self):
        # Logic to stop the traffic generation
        traffic_update.info("Stopping traffic generation.")

    def start_traffic_generation(self):
        # Logic to start the traffic generation with new parameters
        traffic_update.info("Starting traffic generation with new parameters.")

    # Function to handle commands from the command queue
    def handle_commands(command_queue, traffic_controller):
        while True:
            command = command_queue.get()
            if command == 'restart':
                traffic_controller.restart_traffic_generation()
                traffic_update.info("Handled 'restart' command.")
    
    def update_parameters(self, new_params):
        self.updated_parameters = new_params
        self.is_updated = True

    def parameters_updated(self):
        return self.is_updated    
    
    def generate_traffic(self, ue):
        from network.ue import UE
        # Determine the type of traffic to generate based on the UE's service type
        if ue.ServiceType.lower() == 'voice':
            return self.generate_voice_traffic()
        elif ue.ServiceType.lower() == 'video':
            return self.generate_video_traffic()
        elif ue.ServiceType.lower() == 'game':
            return self.generate_gaming_traffic()
        elif ue.ServiceType.lower() == 'iot':
            return self.generate_iot_traffic()
        elif ue.ServiceType.lower() == 'data':
            return self.generate_data_traffic()
        else:
            raise ValueError(f"Unknown service type: {ue.ServiceType}")           
    
    def update_voice_traffic(self, bitrate_range):
        try:
            with self.lock:
                self.voice_traffic_params['bitrate'] = bitrate_range
                traffic_update.info(f"Voice traffic parameters updated to {bitrate_range}")
                return True
        except Exception as e:
            traffic_update.error(f"Failed to update voice traffic parameters: {e}")
            return False

    def update_video_traffic(self, num_streams_range, stream_bitrate_range):
        try:
            with self.lock:
                self.video_traffic_params['num_streams'] = num_streams_range
                self.video_traffic_params['stream_bitrate'] = stream_bitrate_range
                traffic_update.info(f"Video traffic parameters updated to streams: {num_streams_range}, bitrate: {stream_bitrate_range}")
                return True
        except Exception as e:
            traffic_update.error(f"Failed to update video traffic parameters: {e}")
            return False

    def update_gaming_traffic(self, bitrate_range):
        try:
            with self.lock:
                self.gaming_traffic_params['bitrate'] = bitrate_range
                traffic_update.info(f"Gaming traffic parameters updated to {bitrate_range}")
                return True
        except Exception as e:
            traffic_update.error(f"Failed to update gaming traffic parameters: {e}")
            return False

    def update_iot_traffic(self, packet_size_range, interval_range):
        try:
            with self.lock:
                self.iot_traffic_params['packet_size'] = packet_size_range
                self.iot_traffic_params['interval'] = interval_range
                traffic_update.info(f"IoT traffic parameters updated to packet size: {packet_size_range}, interval: {interval_range}")
            return True
        except Exception as e:
            traffic_update.error(f"Failed to update IoT traffic parameters: {e}")
        return False

    def update_data_traffic(self, bitrate_range, interval_range):
        try:
            with self.lock:
                self.data_traffic_params['bitrate'] = bitrate_range
                self.data_traffic_params['interval'] = interval_range
                traffic_update.info(f"Data traffic parameters updated to bitrate: {bitrate_range}, interval: {interval_range}")
                return True
        except Exception as e:
            traffic_update.error(f"Failed to update data traffic parameters: {e}")
        return False
    
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
##############################################################################################################################
    # Traffic generation methods with conditional application of jitter, delay, and packet loss
    def generate_voice_traffic(self):
        # Record the start timestamp
        start_time = datetime.datetime.now()
        time.sleep(self.voice_delay)  # Use voice-specific delay
        jitter = random.uniform(0, self.voice_jitter) if self.voice_jitter > 0 else 0
        bitrate = random.uniform(*self.voice_traffic_params['bitrate'])  # in Kbps
        interval = 0.02  # Interval duration in seconds
        data_size = (bitrate * interval) / 8  # Convert to KB
        #cell_logger.info(f"Voice Traffic: Data Size: {data_size}KB, Interval: {interval}s, Delay: {self.voice_delay}ms, Jitter: {jitter}ms, Packet Loss Rate: {self.voice_packet_loss_rate}%")
        
        # Apply jitter
        time.sleep(jitter)

        # Simulate packet loss
        packet_loss_occurred = random.random() < self.voice_packet_loss_rate

        if packet_loss_occurred:
            data_size = 0  # Packet is lost

        # Record the end timestamp
        end_time = datetime.datetime.now()

        traffic_data = {
            'data_size': data_size,
            'start_timestamp': start_time,
            'end_timestamp': end_time,
            'interval': interval,
            'delay': self.voice_delay,
            'jitter': jitter,
            'packet_loss_rate': self.voice_packet_loss_rate
        }

        return traffic_data
###################################################################################################################
    def generate_video_traffic(self):
        # Record the start timestamp
        start_time = datetime.datetime.now()

        time.sleep(self.video_delay)  # Use video-specific delay
        jitter = random.uniform(0, self.video_jitter) if self.video_jitter > 0 else 0
        time.sleep(jitter)  # Apply jitter

        num_streams = random.randint(*self.video_traffic_params['num_streams'])
        data_size = 0  # in MB
        interval = 1  # Interval duration in seconds

        for _ in range(num_streams):
            stream_bitrate = random.uniform(*self.video_traffic_params['stream_bitrate'])  # in Mbps
            if random.random() < self.video_packet_loss_rate:
                continue  # Skip this stream due to packet loss
            data_size += (stream_bitrate * interval) / 8  # Convert to MB

        # Record the end timestamp
        end_time = datetime.datetime.now()

        traffic_data = {
            'data_size': data_size,  # Total data size of all streams
            'start_timestamp': start_time,
            'end_timestamp': end_time,
            'num_streams': num_streams,
            'interval': interval,
            'delay': self.video_delay,
            'jitter': jitter,
            'packet_loss_rate': self.video_packet_loss_rate
        }

        return traffic_data
###################################################################################################################
    def generate_gaming_traffic(self):
        try:
            # Record the start timestamp
            start_time = datetime.datetime.now()

            time.sleep(self.gaming_delay)  # Use gaming-specific delay
            jitter = random.uniform(0, self.gaming_jitter) if self.gaming_jitter > 0 else 0
            bitrate = random.uniform(*self.gaming_traffic_params['bitrate'])  # in Kbps
            interval = 0.1  # Interval duration in seconds
            data_size = (bitrate * interval) / 8  # Convert to KB

            # Apply jitter
            time.sleep(jitter)

            # Simulate packet loss
            packet_loss_occurred = random.random() < self.gaming_packet_loss_rate
            if packet_loss_occurred:
                data_size = 0  # Packet is lost

            # Record the end timestamp
            end_time = datetime.datetime.now()

            traffic_data = {
                'data_size': data_size,
                'start_timestamp': start_time,
                'end_timestamp': end_time,
                'interval': interval,
                'delay': self.gaming_delay,
                'jitter': jitter,
                'packet_loss_rate': self.gaming_packet_loss_rate
            }

            return traffic_data

        except Exception as e:
            traffic_update.error(f"Failed to generate gaming traffic: {e}")
            # Handle the exception by returning a default data structure
            return {
                'data_size': 0,
                'start_timestamp': datetime.datetime.now(),
                'end_timestamp': datetime.datetime.now(),
                'interval': 0.1,
                'delay': self.gaming_delay,
                'jitter': 0,
                'packet_loss_rate': self.gaming_packet_loss_rate
            }
###########################################################################################
    def generate_iot_traffic(self):
        # Record the start timestamp
        start_time = datetime.datetime.now()

        time.sleep(self.iot_delay)  # Use IoT-specific delay
        jitter = random.uniform(0, self.iot_jitter) if self.iot_jitter > 0 else 0
        packet_size = random.randint(*self.iot_traffic_params['packet_size'])  # in KB
        interval = random.uniform(*self.iot_traffic_params['interval'])  # in seconds
        data_size = packet_size  # Already in KB, no need for conversion

        # Apply jitter
        time.sleep(jitter)

        # Simulate packet loss
        if random.random() < self.iot_packet_loss_rate:
            data_size = 0  # Packet is lost

        # Record the end timestamp
        end_time = datetime.datetime.now()

        traffic_data = {
            'data_size': data_size,
            'start_timestamp': start_time,
            'end_timestamp': end_time,
            'interval': interval,
            'delay': self.iot_delay,
            'jitter': jitter,
            'packet_loss_rate': self.iot_packet_loss_rate
        }

        return traffic_data
###########################################################################################
    def generate_data_traffic(self):
        # Record the start timestamp
        start_time = datetime.datetime.now()

        time.sleep(self.data_delay)  # Use data-specific delay
        jitter = random.uniform(0, self.data_jitter) if self.data_jitter > 0 else 0
        bitrate = random.uniform(*self.data_traffic_params['bitrate'])  # in Mbps
        interval = random.uniform(*self.data_traffic_params['interval'])  # in seconds
        data_size = (bitrate * interval) / 8  # Convert to MB

        # Apply jitter
        time.sleep(jitter)

        # Simulate packet loss
        if random.random() < self.data_packet_loss_rate:
            data_size = 0  # Packet is lost

        # Record the end timestamp
        end_time = datetime.datetime.now()

        traffic_data = {
            'data_size': data_size,
            'start_timestamp': start_time,
            'end_timestamp': end_time,
            'interval': interval,
            'delay': self.data_delay,
            'jitter': jitter,
            'packet_loss_rate': self.data_packet_loss_rate
        }

        return traffic_data
###########################################################################################
    @staticmethod
    def handle_commands(command_queue, traffic_controller):
        while True:
            command = command_queue.get()
            if command == 'restart':
                traffic_controller.restart_traffic_generation()
                traffic_update.info("Handled 'restart' command.")
                
    # Function to start the command handler in a separate thread
    def start_command_handler(self):
        command_handler_thread = Thread(target=TrafficController.handle_commands, args=(self.command_queue, self))
        command_handler_thread.daemon = True
        command_handler_thread.start() 
###########################################################################################
    def get_traffic_parameters(self, ue):
        return {
            'jitter': ue.jitter,
            'packet_loss': ue.packet_loss,
            'delay': ue.delay
        }