from flask import Flask, request, jsonify
import json
import subprocess
import psutil
import netifaces as ni
# import requests
import time
import threading
import csv

version = "1.0.2"

app = Flask(__name__)

## WRITE TO LOG FILE
def write_log(output):
    try:
        with open('/home/pi/automate-update/log.csv', 'a', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow([int(time.time() * 1000), output])

        print("Data written to", file_path)
    
    except Exception as e:
        print("Error:", e)
        
## READ LOG FILE
def read_log():
    data = []
    try:
        with open('/home/pi/automate-update/log.csv', 'r') as file:
            csv_reader = csv.reader(file)
            headers = next(csv_reader)  # Read and ignore the header row
            for row in csv_reader:
                data.append(row)
            
    except Exception as e:
        print("Error:", e)
    
    return data		

## GET LOG FILE
@app.route('/log', methods=['GET'])
def get_log():
    data = read_log()
    return jsonify(data)

## CLEAR LOG FILE
@app.route('/clear_log', methods=['GET'])
def clear_log():
    try:
        result = subprocess.Popen(['rm', '-f', '/home/pi/automate-update/log.csv'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = result.communicate()
        output = stdout + '\n' + stderr
        print(output)
        write_log(output)
        return jsonify(success=True, message="Clear Log Task Set ", data=output)
    except Exception as e:
        return str(e), 500	



## GET MEMORY USAGE
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

## GET DISK USAGE
def get_disk_usage():
    disk = psutil.disk_usage('/')
    return {
        "total_disk": disk.total,
        "used_disk": disk.used,
        "free_disk": disk.free,
        "disk_percent": disk.percent,
        "disk_unit": "bytes"
    }

## GET CPU USAGE
def get_cpu_usage():
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "cpu_unit": "percent"
    }

## GET NETWORK INFO
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

## GET SERIAL NUMBER
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

## CHECK STATUS
@app.route('/status', methods=['GET'])
def check_status():
	return jsonify(success=True, message="Update Server is Running Version " + version)

## UPDATE SERVER SOFTWARE
@app.route('/update_server', methods=['GET'])
def update_server():
    try:
        result = subprocess.Popen(['sudo', 'git', 'pull', '--no-rebase'], cwd='/home/pi/automate-update', stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = result.communicate()
        output = stdout + '\n' + stderr
        print(output)
        write_log(output)
        return jsonify(success=True, message="Update Server - Update Task Set ", data=output)
    except Exception as e:
        return str(e), 500	

def update_server():
    # Add a delay to allow the server to respond first
    time.sleep(5)
    result = subprocess.Popen(['sudo', 'systemctl', 'restart', 'update_server'], cwd='/home/pi/automate-update', stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = result.communicate()
    output = stdout + '\n' + stderr
    print(output)
    write_log(output)

## RESTART UPDATE SERVER SOFTWARE
@app.route('/restart_server', methods=['GET'])
def update_server_application():
    try:
        update_thread = threading.Thread(target=update_server)
        update_thread.start()
        return jsonify(success=True, message="Update Server Restart Task Set")
    except Exception as e:
        return str(e), 500		

## UPDATE AUTOMATE SOFTWARE
def update_automate(image):
    # Add a delay to allow the server to respond first
    time.sleep(5)
    # Pull the latest version of the application
    result = subprocess.Popen(['sudo', 'docker-compose', 'pull', image], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = result.communicate()
    output = stdout + '\n' + stderr
    print(output)
    write_log(output)
    # Remove old images to save space
    result2 = subprocess.Popen(['sudo', 'docker', 'images', 'prune'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = result2.communicate()
    output = stdout + '\n' + stderr
    print(output)
    write_log(output)

@app.route('/update_automate', methods=['GET'])
def update_application():
    try:
		# Run the automate-update.sh script
		# Extract the 'image' query parameter
        image = request.args.get('image')
        if image is None:
            return jsonify(success=False, error="Missing 'image' parameter"), 400
        
        update_thread = threading.Thread(target=update_automate, args=(image,))
        update_thread.start()
        return jsonify(success=True, data="Automate Update Task Set")
    except Exception as e:
        return str(e), 500
    
## STOP AUTOMATE SOFTWARE
@app.route('/stop_automate', methods=['GET'])
def stop_application():
    try:
        result = subprocess.Popen(['sudo', 'docker-compose', '-f', '/home/pi/automate-node/docker-compose.yaml', 'stop', 'automate-node'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = result.communicate()
        output = stdout + '\n' + stderr
        print(output)
        write_log(output)
        return jsonify(success=True, message="Automate Stop Task Set", data=output)
    except Exception as e:
        return str(e), 500	
        
## START AUTOMATE SOFTWARE
@app.route('/start_automate', methods=['GET'])
def start_application():
    try:
        result = subprocess.Popen(['sudo', 'docker-compose', '-f', '/home/pi/automate-node/docker-compose.yaml', 'up', '-d', '--remove-orphans'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = result.communicate()
        output = stdout + '\n' + stderr
        print(output)
        write_log(output)    
        return jsonify(success=True, message="Automate Start Task Set", data=output)
    except Exception as e:
        return str(e), 500	
        
## RESTART AUTOMATE SOFTWARE
@app.route('/restart_automate', methods=['GET'])
def restart_application():
    try:
        result = subprocess.Popen(['sudo', 'docker-compose', '-f', '/home/pi/automate-node/docker-compose.yaml', 'restart', 'automate-node'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = result.communicate()
        output = stdout + '\n' + stderr
        print(output)
        write_log(output)
        return jsonify(success=True, message="Automate Restart Task Set", data=output)
    except Exception as e:
        return str(e), 500			
        
## GET SYSTEM INFO
@app.route('/systeminfo', methods=['GET'])
def system_info():
    try:
        memory_usage = get_memory_usage()
        disk_usage = get_disk_usage()
        cpu_usage = get_cpu_usage()
        network_info = get_network_info()
        serial_number = get_serial_number()
        system_info = {
            "updateserver_version": version,
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
        return jsonify(success=True, data=system_info)
    except Exception as e:
        return str(e), 500

## REBOOT RASPBERRY PI
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

## RUN UPDATE SERVER APPLICATION
if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8086)

