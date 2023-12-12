#system_resources.py
#This file located in health check directory
import psutil

def check_system_resources():
    # Placeholder for actual system resource check logic
    cpu_usage = psutil.cpu_percent()
    memory_usage = psutil.virtual_memory().percent
    return {
        'cpu_usage': f'{cpu_usage}%',
        'memory_usage': f'{memory_usage}%'
    }

if __name__ == "__main__":
    resources = check_system_resources()
    print(resources)