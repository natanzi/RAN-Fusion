#this is sector.py in network folder
class Sector:
    def __init__(self, sector_id, cell_id, azimuth_angle, beamwidth, frequency, duplex_mode, tx_power, bandwidth, mimo_layers, beamforming, ho_margin, load_balancing):
        self.sector_id = sector_id
        self.cell_id = cell_id
        self.azimuth_angle = azimuth_angle
        self.beamwidth = beamwidth
        self.frequency = frequency
        self.duplex_mode = duplex_mode
        self.tx_power = tx_power
        self.bandwidth = bandwidth
        self.mimo_layers = mimo_layers
        self.beamforming = beamforming
        self.ho_margin = ho_margin
        self.load_balancing = load_balancing

    @classmethod
    def from_json(cls, data):
        return cls(**data)

    def serialize_for_influxdb(self):
        # This method should return a data structure that is compatible with your InfluxDB schema
        # The following is a placeholder example
        return {
            'measurement': 'sector',
            'tags': {
                'sector_id': self.sector_id,
                'cell_id': self.cell_id
            },
            'fields': {
                'azimuth_angle': self.azimuth_angle,
                'beamwidth': self.beamwidth,
                'frequency': self.frequency,
                'duplex_mode': self.duplex_mode,
                'tx_power': self.tx_power,
                'bandwidth': self.bandwidth,
                'mimo_layers': self.mimo_layers,
                'beamforming': int(self.beamforming),  # Convert boolean to int for InfluxDB
                'ho_margin': self.ho_margin,
                'load_balancing': self.load_balancing
            }
        }