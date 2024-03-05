################################################################################################################################################
# this is sectory.py which is located in network directory. The Sector class represents a sector within a cell in a cellular network.           #
# Sectors are subdivisions of a cell site where each sector covers a certain area and is equipped with its own set of antennas,                 #
# frequency bands, and power settings to manage the network's radio resources efficiently. This class is designed to simulate the               #
# behavior and characteristics of real-world network sectors, including managing connections to User Equipments (UEs), handling                 #
# sector-specific configurations, and reporting metrics for network simulation and analysis.You can extend this class with additional           #
# methods to handle sector-specific logic, such as calculating signal strength, managing handovers, or adjusting parameters for load balancing. #
# Remember to test this class thoroughly to ensure it integrates well with the rest of code.                                                    #
#################################################################################################################################################

global all_sectors 
all_sectors = {}
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS, WritePrecision
import time
import uuid
import threading
from logs.logger_config import sector_logger,database_logger
from database.database_manager import DatabaseManager
from network.ue import UE
sector_lock = threading.Lock()
from datetime import datetime

# Assume a global list or set for UE IDs is defined at the top level of your module
global_ue_ids = set()
sector_instances = {}

class Sector:
    def __init__(self, sector_id, cell_id, cell, capacity, azimuth_angle, beamwidth, frequency, duplex_mode, tx_power, bandwidth, mimo_layers, beamforming, ho_margin, load_balancing, max_throughput, channel_model=None, connected_ues=None, current_load=0, ssb_periodicity=None, ssb_offset=0, is_active=True, sector_count=0):
        self.sector_id = sector_id  # String, kept as is for identifiers
        self.instance_id = str(uuid.uuid4())  # Generic unique identifier for the instance of the sector
        sector_instances[sector_id] = self     # Add the sector to the global dictionary
        self.cell_id = cell_id  # String, kept as is for identifiers
        self.cell = cell  # Cell object, no change needed
        self.ues = {}  # Add a dictionary to track UEs mapped to their IDs
        # Numeric fields optimized based on usage
        self.capacity = int(capacity)  # Integer, as capacity is a count
        self.remaining_capacity = int(capacity)  # Initialize remaining_capacity with the total capacity
        self.azimuth_angle = int(azimuth_angle)  # Integer, as angles can be represented without decimal precision
        self.beamwidth = int(beamwidth)  # Integer, as beamwidth can be represented without decimal precision
        self.frequency = float(frequency)  # Float, as frequency may require decimal precision
        self.tx_power = int(tx_power)  # Integer, assuming power levels can be integers
        self.bandwidth = int(bandwidth)  # Integer, assuming bandwidth can be represented without decimal precision
        self.mimo_layers = int(mimo_layers)  # Integer, as layer count is a whole number
        self.beamforming = bool(beamforming)  # Boolean, kept as is
        self.ho_margin = int(ho_margin)  # Integer, assuming handover margin can be represented without decimal precision
        self.load_balancing = int(load_balancing)  # Integer, assuming load balancing metrics can be integers
        self.duplex_mode = duplex_mode
        self.max_throughput = max_throughput  # Maximum data handling capacity in bps (value is available in sector config)
        self.channel_model = channel_model
        self.sector_count = sector_count
        self.ssb_periodicity = ssb_periodicity
        self.ssb_offset = ssb_offset
        self.is_active = is_active
        self.sector_load_attribute = 0 # Update the sector's load attribute

        # List of UEs and current load, no change needed
        self.connected_ues = connected_ues if connected_ues is not None else []
        self.current_load = int(current_load)  # Integer, as load is a count which is shoe that how many use hosted in this sector.

    @classmethod
    def from_json(cls, data, cell):
    # Ensure the 'capacity' key exists in data, if not, set a default value or handle it appropriately
        if 'capacity' not in data:
            # Handle the missing 'capacity' key, for example by setting a default value
            data['capacity'] = 3  # Replace with an actual default value or raise an error
        else:
            data['capacity'] = int(data['capacity'])  # Ensure capacity is an integer

        # The 'cell' object is passed as an argument, so we set it directly
        data['cell'] = cell

        # The 'cell_id' is obtained from the 'cell' object
        data['cell_id'] = cell.ID

        return cls(**data)
    
    def serialize_for_influxdb(self):
        try:
            unix_timestamp_seconds = int(datetime.utcnow().timestamp())
            ssb_periodicity_value = self.ssb_periodicity if self.ssb_periodicity is not None else 0
            point = Point("sector_metrics") \
                .tag("sector_id", str(self.sector_id)) \
                .tag("cell_id", str(self.cell_id)) \
                .tag("gnodeb_id", str(self.cell.gNodeB_ID)) \
                .tag("entity_type", "sector") \
                .tag("instance_id", str(self.instance_id)) \
                .field("frequency", float(self.frequency)) \
                .field("duplex_mode", str(self.duplex_mode)) \
                .field("tx_power", int(self.tx_power)) \
                .field("bandwidth", int(self.bandwidth)) \
                .field("mimo_layers", int(self.mimo_layers)) \
                .field("beamforming", bool(self.beamforming)) \
                .field("ho_margin", int(self.ho_margin)) \
                .field("load_balancing", int(self.load_balancing)) \
                .field("max_ues", int(self.capacity)) \
                .field("max_throughput", int(self.max_throughput)) \
                .field("channel_model", str(self.channel_model)) \
                .field("sector_is_active", bool(self.is_active)) \
                .field("sector_count", int(self.sector_count)) \
                .field("is_active", bool(self.is_active)) \
                .field("sector_load", float(self.sector_load_attribute)) \
                .time(unix_timestamp_seconds, WritePrecision.S)

            return point
        except Exception as e:
            database_logger.error(f"Error serializing sector data for InfluxDB: {e}")
            # Depending on your error handling policy, you might want to re-raise the exception or return None
            raise

    def add_ue(self, ue):
        with sector_lock:  # Assuming sector_lock is correctly defined and accessible
            # Check if the sector is at its maximum capacity
            if len(self.connected_ues) >= self.capacity:
                sector_logger.warning(f"Sector {self.sector_id} at max capacity! Cannot add UE {ue.ID}")
                return  # Important to return here to avoid adding the UE when the sector is full

            # Check if the UE is already connected to the sector
            if ue.ID in self.connected_ues:
                sector_logger.warning(f"UE with ID {ue.ID} is already connected to the sector {self.sector_id}.")
                return  # Similarly, return here to avoid re-adding an existing UE

            # If the checks pass, proceed to add the UE
            self.connected_ues.append(ue.ID)  # Store only the ID, not the UE object
            self.current_load += 1  # Increment the current load
            self.cell.update_ue_lists()  # Assuming this method correctly updates relevant UE lists in the cell
            global_ue_ids.add(ue.ID)  # Add the UE ID to the global list (ensure this is defined and accessible)
            self.remaining_capacity = self.capacity - len(self.connected_ues)  # Update remaining capacity
            # Set the connected_sector attribute for the UE
            ue.connected_sector = self.sector_id  # This line sets the UE's connected sector
            ue.ConnectedCellID = self.cell_id  # Ensure self.cell_id is correctly defined and accessible
            ue.gNodeB_ID = self.cell.gNodeB_ID  # Ensure self.cell and its gNodeB_ID are correctly defined and accessible
            self.ues[ue.ID] = ue  # Add the UE object to the sector's UE dictionary
            # Note: The global_ue_ids.add(ue.ID) call is duplicated in original code. It should only be necessary once.

            # Serialize the sector for InfluxDB and insert the data
            point = self.serialize_for_influxdb()  # Ensure this method correctly serializes the sector's data
            DatabaseManager().insert_data(point)  # Ensure DatabaseManager is correctly implemented and accessible

            sector_logger.info(f"UE with ID {ue.ID} has been added to the sector {self.sector_id}. Current UE Load count: {self.current_load}")

    def remove_ue(self, ue_id):
        with sector_lock:
            if ue_id in self.connected_ues:
                self.connected_ues.remove(ue_id)  # Correctly remove the ID string
                self.current_load -= 1  # Decrement the current load
                self.cell.update_ue_lists()
                global_ue_ids.discard(ue_id)  # Correctly discard the ID string
                self.remaining_capacity = self.capacity - len(self.connected_ues)  # Update remaining_capacity
                del self.ues[ue_id]  # Correctly delete the UE from the dictionary
                point = self.serialize_for_influxdb()
                DatabaseManager().insert_data(point)
                sector_logger.info(f"UE with ID {ue_id} has been removed from the sector. Current load (count): {self.current_load}")
            
                # Now also deregister the UE from the global tracking structures
                UE.deregister_ue(ue_id)
        
            else:
                sector_logger.warning(f"UE with ID {ue_id} is not connected to the sector.")
                
    @classmethod
    def get_sector_by_id(cls, sector_id):
        db_manager = DatabaseManager.get_instance()
        sector_data = db_manager.get_sector_by_id(sector_id)
        if sector_data:
            return cls.from_json(sector_data)  # Assuming a method to create a Sector instance from data
        return None
    
    