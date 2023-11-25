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
        return Cell(
            cell_id=json_data["cell_id"],
            gnodeb_id=json_data["gnodeb_id"],
            frequencyBand=json_data["frequencyBand"],
            duplexMode=json_data["duplexMode"],
            tx_power=json_data["tx_power"],
            bandwidth=json_data["bandwidth"],
            ssb_periodicity=json_data["ssbPeriodicity"],
            ssb_offset=json_data["ssbOffset"],
            max_connect_ues=json_data["maxConnectUes"],
            channel_model=json_data["channelModel"],
            trackingArea=json_data.get("trackingArea")
        )

    def add_ue(self, ue):
        if len(self.ConnectedUEs) < self.MaxConnectedUEs:
            self.ConnectedUEs.append(ue)
        else:
            raise Exception("Maximum number of connected UEs reached for this cell.")