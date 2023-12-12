#This file located in health check directory
import os

def check_server_status():
    # Placeholder for actual server status check logic
    uptime = os.popen('uptime').readline()
    return {
        'status': 'UP',
        'uptime': uptime
    }

if __name__ == "__main__":
    status = check_server_status()
    print(status)