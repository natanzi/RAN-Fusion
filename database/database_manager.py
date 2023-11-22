#database_manager.py in database directory
import sqlite3

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def connect(self):
        """Establishes a database connection."""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS ue_kpi (
                          timestamp TEXT, ue_id TEXT, imsi TEXT, latency REAL, throughput REAL,
                          congestion_status BOOLEAN)''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS gnodeb_kpi (
                          timestamp TEXT, gnodeb_id TEXT, imsi TEXT, latency REAL, throughput REAL,
                          congestion_status BOOLEAN)''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS cell_kpi (
                          timestamp TEXT, cell_id TEXT, imsi TEXT, latency REAL, throughput REAL,
                          congestion_status BOOLEAN)''')

        # New table to capture all KPI data
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS all_kpi_data (
                          timestamp TEXT, ue_id TEXT, imsi TEXT, latency REAL, throughput REAL,
                          congestion_status BOOLEAN, cell_id TEXT, gnodeb_id TEXT)''')

        # Create a view named 'RAN_Report' based on the 'all_kpi_data' table
        self.cursor.execute('''CREATE VIEW IF NOT EXISTS RAN_Report AS
                               SELECT timestamp, ue_id, imsi, latency, throughput, 
                               congestion_status, cell_id, gnodeb_id
                               FROM all_kpi_data''')

    def insert_ue_data(self, data):
        """Inserts a row of UE KPI data into the ue_kpi table."""
        self.cursor.execute('''INSERT INTO ue_kpi (timestamp, ue_id, imsi, latency, throughput, 
                              congestion_status) VALUES (?, ?, ?, ?, ?, ?)''', data)

    def insert_gnodeb_data(self, data):
        """Inserts a row of gNodeB KPI data into the gnodeb_kpi table."""
        self.cursor.execute('''INSERT INTO gnodeb_kpi (timestamp, gnodeb_id, imsi, latency, throughput, 
                              congestion_status) VALUES (?, ?, ?, ?, ?, ?)''', data)

    def insert_cell_data(self, data):
        """Inserts a row of Cell KPI data into the cell_kpi table."""
        self.cursor.execute('''INSERT INTO cell_kpi (timestamp, cell_id, imsi, latency, throughput, 
                              congestion_status) VALUES (?, ?, ?, ?, ?, ?)''', data)

    def insert_all_kpi_data(self, data):
        """Inserts a row of data into the all_kpi_data table."""
        self.cursor.execute('''INSERT INTO all_kpi_data (timestamp, ue_id, imsi, latency, throughput, 
                              congestion_status, cell_id, gnodeb_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', data)

    def commit_changes(self):
        """Commits changes to the database."""
        self.conn.commit()

    def close_connection(self):
        """Closes the database connection."""
        self.conn.close()

