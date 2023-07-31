import psutil
import json
import netifaces as ni
import requests
import time

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

def post_system_info(system_info):
    url = "http://localhost:8085/api/v1/systeminfo"
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url, json.dumps(system_info), headers=headers)
    if response.status_code != 200:
        print(f"Failed to post system info. Status code: {response.status_code}")
        
        # print("System info posted successfully.")
    return response

def main():
    while True:
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
            "mac_address": network_info["mac_address"],
            "timestamp": int(time.time())
        }
        json_output = json.dumps(system_info, indent=4)
        response = post_system_info(system_info)
        # print(json_output)
        # Output the response content
        # if response:
            # print("Response Content:")
            # print(response.json())
        time.sleep(10)
    	
if __name__ == "__main__":
    main()
