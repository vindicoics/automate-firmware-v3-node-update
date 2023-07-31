from flask import Flask, jsonify
import json
import subprocess

app = Flask(__name__)

@app.route('/status', methods=['GET'])
def check_status():
	return jsonify(success=True, data="Update Server is Running")

@app.route('/update', methods=['GET'])
def update_application():
	try:
		# Run the automate-update.sh script
		subprocess.run(['sh', '/home/pi/automate-node/automate-update.sh'], capture_output=True, text=True)
		# if result.returncode == 0:
		return jsonify(success=True, data="Automate Update Task Set")
		# else:
		# 	return "Error updating application: " + result.stderr, 500
	except Exception as e:
		return str(e), 500

@app.route('/reboot', methods=['GET'])
def reboot_raspberry_pi():
	try:
		# Run the command to reboot the Raspberry Pi
		subprocess.run(['sudo', 'reboot'])
		return jsonify(success=True, data="Raspberry Pi is rebooting...")
	except Exception as e:
		return str(e), 500

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8086)

