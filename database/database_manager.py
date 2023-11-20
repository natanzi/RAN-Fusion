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


    def insert_ue_data(self, data):
        """Inserts a row of UE KPI data into the ue_kpi table."""
        self.cursor.execute('''INSERT INTO ue_kpi (timestamp, ue_id, latency, throughput, 
                              congestion_status) VALUES (?, ?, ?, ?, ?)''', data)

    def insert_gnodeb_data(self, data):
        """Inserts a row of gNodeB KPI data into the gnodeb_kpi table."""
        self.cursor.execute('''INSERT INTO gnodeb_kpi (timestamp, gnodeb_id, latency, throughput, 
                              congestion_status) VALUES (?, ?, ?, ?, ?)''', data)

    def insert_cell_data(self, data):
        """Inserts a row of Cell KPI data into the cell_kpi table."""
        self.cursor.execute('''INSERT INTO cell_kpi (timestamp, cell_id, latency, throughput, 
                              congestion_status) VALUES (?, ?, ?, ?, ?)''', data)

    def commit_changes(self):
        """Commits changes to the database."""
        self.conn.commit()

    def close_connection(self):
        """Closes the database connection."""
        self.conn.close()

