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
        # Logging statement should be here, after all attributes are set
        logging.info(f"Cell '{self.ID}' has been created in gNodeB '{self.gNodeB_ID}' with max capacity {self.MaxConnectedUEs}.")
        
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
    def to_dict(self):
        return {
            'ID': self.ID,
            'gNodeB_ID': self.gNodeB_ID,
            'FrequencyBand': self.FrequencyBand,
            'DuplexMode': self.DuplexMode,
            'TxPower': self.TxPower,
            'Bandwidth': self.Bandwidth,
            'SSBPeriodicity': self.SSBPeriodicity,
            'SSBOffset': self.SSBOffset,
            'MaxConnectedUEs': self.MaxConnectedUEs,
            'ChannelModel': self.ChannelModel,
            'TrackingArea': self.TrackingArea,
            # Assuming you don't need to include the 'ConnectedUEs' list
        }
    def add_ue(self, ue):
        if len(self.ConnectedUEs) < self.MaxConnectedUEs:
            self.ConnectedUEs.append(ue)
            print(f"UE '{ue.ID}' has been attached to Cell '{self.ID}'.")
        else:
            raise Exception("Maximum number of connected UEs reached for this cell.")