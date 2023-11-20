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
            frequencyBand=item["frequencyBand"],  # Corrected to match constructor parameter
            duplexMode=item["duplexMode"],        # Corrected to match constructor parameter
            tx_power=item["txPower"],             # Corrected to match constructor parameter
            bandwidth=item["bandwidth"],
            ssb_periodicity=item["ssbPeriodicity"],  # Corrected to match constructor parameter
            ssb_offset=item["ssbOffset"],            # Corrected to match constructor parameter
            max_connect_ues=item["maxConnectUes"],   # Corrected to match constructor parameter
            channel_model=item["channelModel"],      # Corrected to match constructor parameter
            trackingArea=item.get("trackingArea")    # Use .get() to avoid KeyError if the key is missing
        )
        cells.append(cell)
    return cells

    #def add_ue(self, ue_id):
        #if ue_id not in self.ConnectedUEs and len(self.ConnectedUEs) < self.MaxConnectedUEs:
            #self.ConnectedUEs.append(ue_id)

    #def remove_ue(self, ue_id):
        #if ue_id in self.ConnectedUEs:
            #self.ConnectedUEs.remove(ue_id)
        

