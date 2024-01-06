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

# Example of loading sectors and associating them with cells
def load_sectors(sector_config_path):
    with open(sector_config_path, 'r') as file:
        sector_config = json.load(file)
    sectors = {}
    for sector_info in sector_config['sectors']:
        sector = Sector(**sector_info)
        sectors[sector.sector_id] = sector
    return sectors

# Assuming cells is a dictionary of Cell objects keyed by cell_id
sectors = load_sectors('path_to_sector_config.json')
for sector in sectors.values():
    cells[sector.cell_id].add_sector(sector)