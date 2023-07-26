import psutil
import json
import netifaces as ni

def get_memory_usage():
    memory = psutil.virtual_memory()
    return {
        "total_memory": memory.total,
        "available_memory": memory.available,
        "used_memory": memory.used,
        "free_memory": memory.free,
        "memory_percent": memory.percent,
        "memory_unit": "bytes"
    }

def get_disk_usage():
    disk = psutil.disk_usage('/')
    return {
        "total_disk": disk.total,
        "used_disk": disk.used,
        "free_disk": disk.free,
        "disk_percent": disk.percent,
        "disk_unit": "bytes"
    }

def get_cpu_usage():
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "cpu_unit": "percent"
    }

def get_network_info():
    # Get the IP and MAC addresses of the Ethernet interface (assumes eth0)
    try:
        iface_info = ni.ifaddresses('eth0')
        ip_address = iface_info[ni.AF_INET][0]['addr']
        mac_address = iface_info[ni.AF_LINK][0]['addr']
    except (ValueError, KeyError):
        ip_address = "N/A"
        mac_address = "N/A"

    return {
        "ip_address": ip_address,
        "mac_address": mac_address
    }

def get_serial_number():
    try:
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if line.startswith('Serial'):
                    serial = line.split(':')[-1].strip()
                    return serial
    except FileNotFoundError:
        return "N/A"

    return "N/A"

def main():
    memory_usage = get_memory_usage()
    disk_usage = get_disk_usage()
    cpu_usage = get_cpu_usage()
    network_info = get_network_info()
    serial_number = get_serial_number()
    system_info = {
        "serial_number": serial_number,
        "total_memory": memory_usage["total_memory"],
        "available_memory": memory_usage["available_memory"],
        "used_memory": memory_usage["used_memory"],
        "free_memory": memory_usage["free_memory"],
        "memory_percent": memory_usage["memory_percent"],
        "memory_unit": memory_usage["memory_unit"],
        "total_disk": disk_usage["total_disk"],
        "used_disk": disk_usage["used_disk"],
        "free_disk": disk_usage["free_disk"],
        "disk_percent": disk_usage["disk_percent"],
        "disk_unit": disk_usage["disk_unit"],
        "cpu_percent": cpu_usage["cpu_percent"],
        "cpu_unit": cpu_usage["cpu_unit"],
        "ip_address": network_info["ip_address"],
        "mac_address": network_info["mac_address"]
    }
    json_output = json.dumps(system_info, indent=4)
    print(json_output)

if __name__ == "__main__":
    main()
