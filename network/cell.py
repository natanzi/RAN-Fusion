#Defines the Cell class, which is part of a gNodeB.// this is located inside network directory
class Cell:
    def __init__(self, cell_id, gnodeb_id, frequencyBand, duplexMode, tx_power, bandwidth, ssb_periodicity, ssb_offset, max_connect_ues, channel_model, trackingArea=None):
        self.ID = cell_id
        self.gNodeB_ID = gnodeb_id
        self.FrequencyBand = frequencyBand
        self.DuplexMode = duplexMode
        self.TxPower = tx_power
        self.Bandwidth = bandwidth
        self.SSBPeriodicity = ssb_periodicity
        self.SSBOffset = ssb_offset
        self.MaxConnectedUEs = max_connect_ues
        self.ChannelModel = channel_model
        self.TrackingArea = trackingArea 
        self.ConnectedUEs = []

@staticmethod
def from_json(json_data):
    cells = []
    for item in json_data["cells"]:
        cell = Cell(
            cell_id=item["cell_id"],
            gnodeb_id=item["gnodeb_id"],
            frequencyBand=item["frequencyBand"],
            duplexMode=item["duplexMode"],
            tx_power=item["txPower"],
            bandwidth=item["bandwidth"],
            ssb_periodicity=item["ssbPeriodicity"],
            ssb_offset=item["ssbOffset"],  # This should match the constructor argument name
            max_connect_ues=item["maxConnectUes"],
            channel_model=item["channelModel"],
            trackingArea=item.get("trackingArea")
    )
        cells.append(cell)
    return cells

    def add_ue(self, ue):
        if len(self.ConnectedUEs) < self.MaxConnectedUEs:
            self.ConnectedUEs.append(ue)
        else:
            raise Exception("Maximum number of connected UEs reached for this cell.")