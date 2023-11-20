#Defines the Cell class, which is part of a gNodeB.// this is located inside network directory
class Cell:
    def __init__(self, cell_id, gnodeb_id, frequency_band, duplex_mode, tx_power, bandwidth, ssb_periodicity, ssb_offset, max_connect_ues, channel_model):
        self.ID = cell_id
        self.gNodeB_ID = gnodeb_id
        self.FrequencyBand = frequency_band
        self.DuplexMode = duplex_mode
        self.TxPower = tx_power
        self.Bandwidth = bandwidth
        self.SSBPeriodicity = ssb_periodicity
        self.SSBOffset = ssb_offset
        self.MaxConnectedUEs = max_connect_ues
        self.ChannelModel = channel_model
        self.ConnectedUEs = []  # Track connected UEs

    @staticmethod
    def from_json(json_data):
        cells = []
        for item in json_data["cells"]:
            cell = Cell(
                cell_id=item["cell_id"],
                gnodeb_id=item["gnodeb_id"],
                frequency_band=item["frequencyBand"],
                duplex_mode=item["duplexMode"],
                tx_power=item["txPower"],
                bandwidth=item["bandwidth"],
                ssb_periodicity=item["ssbPeriodicity"],
                ssb_offset=item["ssbOffset"],
                max_connect_ues=item["maxConnectUes"],
                channel_model=item["channelModel"]
            )
            cells.append(cell)
        return cells

    def add_ue(self, ue_id):
        if ue_id not in self.ConnectedUEs and len(self.ConnectedUEs) < self.MaxConnectedUEs:
            self.ConnectedUEs.append(ue_id)

    def remove_ue(self, ue_id):
        if ue_id in self.ConnectedUEs:
            self.ConnectedUEs.remove(ue_id)
        

