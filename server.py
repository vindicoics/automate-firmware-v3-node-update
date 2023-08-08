from flask import Flask, jsonify
import json
import subprocess
import psutil
import netifaces as ni
import requests
import time
import threading

app = Flask(__name__)

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

@app.route('/status', methods=['GET'])
def check_status():
	return jsonify(success=True, data="Update Server is Running")

def update_automate():
    # Add a delay to allow the server to respond first
    time.sleep(5)
    # Execute the reboot command
    subprocess.run(['sh', '/home/pi/automate-node/automate-update.sh'], capture_output=False)

@app.route('/update', methods=['GET'])
def update_application():
    try:
		# Run the automate-update.sh script
        update_thread = threading.Thread(target=update_automate)
        update_thread.start()
		# if result.returncode == 0:
        return jsonify(success=True, data="Automate Update Task Set")
		# else:
		# 	return "Error updating application: " + result.stderr, 500
    except Exception as e:
        return str(e), 500
    
def stop_automate():
    # Add a delay to allow the server to respond first
    time.sleep(5)
    # Execute the reboot command
    subprocess.run(['sh', '/home/pi/automate-node/automate-stop.sh'], capture_output=False)

@app.route('/stop', methods=['GET'])
def stop_application():
    try:
		# Run the automate-update.sh script
        # stop_thread = threading.Thread(target=stop_automate)
        # stop_thread.start()
        result = subprocess.run(['sh', '/home/pi/automate-node/automate-stop.sh'], capture_output=True stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result.stdout)
		# if result.returncode == 0:
        return jsonify(success=True, data="Automate Stop Task Set", result=result.stdout)
		# else:
		# 	return "Error updating application: " + result.stderr, 500
    except Exception as e:
        return str(e), 500	
        
def start_automate():
    # Add a delay to allow the server to respond first
    time.sleep(5)
    # Execute the reboot command
    subprocess.run(['sh', '/home/pi/automate-node/automate-start.sh'], capture_output=False)

@app.route('/start', methods=['GET'])
def start_application():
    try:
		# Run the automate-update.sh script
        start_thread = threading.Thread(target=start_automate)
        start_thread.start()
		# if result.returncode == 0:
        return jsonify(success=True, data="Automate Start Task Set")
		# else:
		# 	return "Error updating application: " + result.stderr, 500
    except Exception as e:
        return str(e), 500	
        
def restart_automate():
    # Add a delay to allow the server to respond first
    time.sleep(5)
    # Execute the reboot command
    subprocess.run(['sh', '/home/pi/automate-node/automate-restart.sh'], capture_output=False)

@app.route('/restart', methods=['GET'])
def restart_application():
    try:
		# Run the automate-update.sh script
        restart_thread = threading.Thread(target=restart_automate)
        restart_thread.restart()
		# if result.returncode == 0:
        return jsonify(success=True, data="Automate Restart Task Set")
		# else:
		# 	return "Error updating application: " + result.stderr, 500
    except Exception as e:
        return str(e), 500			
        
@app.route('/systeminfo', methods=['GET'])
def system_info():
    try:
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
            "timestamp": int(time.time() * 1000)
        }
        # json_output = json.dumps(system_info, indent=4)
        return jsonify(success=True, data=system_info)
    except Exception as e:
        return str(e), 500

def reboot_server():
    # Add a delay to allow the server to respond first
    time.sleep(10)
    # Execute the reboot command
    subprocess.run(['sudo', 'reboot'])

@app.route('/reboot', methods=['GET'])
def reboot_raspberry_pi():
    try:
	    # Start a new thread for the reboot process
        reboot_thread = threading.Thread(target=reboot_server)
        reboot_thread.start()
        return jsonify(success=True, data="Raspberry Pi is rebooting...")
    except Exception as e:
         return str(e), 500

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8086)

