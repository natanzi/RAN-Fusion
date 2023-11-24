#init_cell.py // this file located in network directory
#Initialization Of the cells

# Initialize Cells and link them to gNodeBs
    cells = [
        Cell(
            cell_id=cell_data['cell_id'],
            gnodeb_id=cell_data['gnodeb_id'],
            frequencyBand=cell_data['frequencyBand'],
            duplexMode=cell_data['duplexMode'],
            tx_power=cell_data['tx_power'], 
            bandwidth=cell_data['bandwidth'],
            ssb_periodicity=cell_data['ssbPeriodicity'], 
            ssb_offset=cell_data['ssbOffset'],
            max_connect_ues=cell_data['maxConnectUes'],
            channel_model=cell_data['channelModel'],
            trackingArea=cell_data.get('trackingArea', None)
        ) for cell_data in cells_config['cells']
    ]

    # Link cells to their respective gNodeBs
    for cell in cells:
        for gnodeb in gNodeBs:
            if cell.gnodeb_id == gnodeb.ID:
                gnodeb.Cells.append(cell)
                break
