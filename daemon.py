'''
FABITMANAGE DAEMON
@mariolatiffathy/fabitmanage-daemon
'''
import subproccess
import threading
import configparser
import time
import mysql.connector
import json
import uuid
import crypt
from flask import Flask, jsonify, request
from pyftpdlib.authorizers import DummyAuthorizer 
from pyftpdlib.handlers import FTPHandler 
from pyftpdlib.servers import FTPServer

# Load daemon configuration file
daemon_config = configparser.ConfigParser()
daemon_config.read("/fabitmanage-daemon/config/daemon.ini")

# Start a MySQL database connection
daemondb = mysql.connector.connect(
  host=daemon_config['db']['host'],
  user=daemon_config['db']['user'],
  passwd=daemon_config['db']['password'],
  database=daemon_config['db']['name']
)

# Variables
daemon_version = "v0.1-alpha"

# Fixed responses
RES_UNAUTHENTICATED = {"error": {"http_code": 403}}

# Init Flask app
app = Flask(__name__)

def IS_AUTHENTICATED(auth_header):
    check_auth_key = daemondb.cursor()
    check_auth_key.execute("SELECT * FROM daemon_keys WHERE key = %s", (auth_header))
    check_auth_key.fetchall()
    if check_auth_key.rowcount == 0:
        return False
    else:
        return True

@app.route('/api')
def api():
    if IS_AUTHENTICATED(request.headers['Authorization']) == False:
        return jsonify(RES_UNAUTHENTICATED), 403
    return jsonify({"error": {"http_code": 405}}), 405

@app.route('/api/v1'):
def api_v1():
    if IS_AUTHENTICATED(request.headers['Authorization']) == False:
        return jsonify(RES_UNAUTHENTICATED), 403
    return jsonify({"error": {"http_code": 405}}), 405
    
@app.route('/api/v1/servers/create', methods=['POST'])
def create_server():
    if IS_AUTHENTICATED(request.headers['Authorization']) == False:
        return jsonify(RES_UNAUTHENTICATED), 403
    req_data = request.get_json()
    required_data = ["allowed_ports", "server_id", "enable_ftp", "ram", "cpu", "disk", "startup_command"]
    for required in required_data:
        if not required in req_data:
            return jsonify({"error": {"http_code": 422, "description": "You are missing a required field."}}), 422
    if "," in req_data['allowed_ports']:
        ports = req_data['allowed_ports'].split(',')
        for port in ports:
            if int(port) > 65535 or int(port) == 0:
                return jsonify({"error": {"http_code": 422, "description": "The port " + port + " is not a 16-bit port."}}), 422
    else:
        if int(req_data['allowed_ports']) > 65535 or int(req_data['allowed_ports']) == 0:
            return jsonify({"error": {"http_code": 422, "description": "The port " + req_data['allowed_ports'] + " is not a 16-bit port."}}), 422
    if req_data['enable_ftp'] != True and req_data['enable_ftp'] != False:
        return jsonify({"error": {"http_code": 422, "description": "enable_ftp must be a boolean."}}), 422
    if int(req_data['ram']) < 32 or int(req_data['ram']) == 0:
        return jsonify({"error": {"http_code": 422, "description": "ram must be an integer greater than or equal to 32."}}), 422
    if int(req_data['cpu']) < 10 or int(req_data['cpu']) == 0:
        return jsonify({"error": {"http_code": 422, "description": "cpu must be an integer greater than or equal to 10."}}), 422
    if int(req_data['disk']) < 3 or int(req_data['disk']) == 0:
        return jsonify({"error": {"http_code": 422, "description": "disk must be an integer greater than or equal to 3."}}), 422
    if not isinstance(req_data['server_id'], str):
        return jsonify({"error": {"http_code": 422, "description": "server_id must be a string."}}), 422
    queue_parameters = json.dumps(req_data)
    queue_action = "create_server"
    queuepush = daemondb.cursor()
    queuepush.execute("INSERT INTO queue (action, parameters, being_processed) VALUES (%s, %s, %s)", (queue_action, queue_parameters, 0))
    daemondb.commit()
    return jsonify({"success": {"http_code" 200, "description": "Server successfully queued for creation."}}), 200
    
def QueueManager():
    while True:
        time.sleep(1)
        queue_cursor = daemondb.cursor()
        queue_cursor.execute("SELECT * FROM queue WHERE being_processed = 0")
        result = queue_cursor.fetchall()
        if queue_cursor.rowcount > 0:
            for queue_item in result:
                update_being_processed = daemondb.cursor()
                update_being_processed.execute("UPDATE queue SET being_processed = 1 WHERE id = %s", (queue_item['id']))
                daemondb.commit()
                
                queue_action = queue_item['action']
                queue_parameters = queue_item['parameters']
                
                if queue_action == "create_server":
                    CONTAINER_ID = "fabitmanage-" + str(uuid.uuid4())
                    subprocess.check_output(["useradd", "-m", "-d", "/home/fabitmanage/daemon-data/" + CONTAINER_ID, "-p", crypt.crypt(uuid.uuid4() + uuid.uuid4()), CONTAINER_ID])
                    
                if queue_action == "delete_server":
                    # TODO: DELETE SERVER ACTION
                    
                delete_queue = daemondb.cursor()
                delete_queue.execute("DELETE FROM queue WHERE id = %s", (queue_item['id']))
                daemondb.commit()
    
def PortBindingPermissions():
    while True:
        time.sleep(1)
        # TODO: Check binded ports permissions

if __name__ == '__main__':
    print("FabitManage Daemon " + daemon_version)
    print("Starting threads & components...")
    # Define & start the daemon threads
    for _ in range(int(daemon_config['threads']['queuemanager_threads'])):
        QueueManager_t = threading.Thread(target=QueueManager, args=())
        QueueManager_t.start()
    for _ in range(int(daemon_config['threads']['portbindingpermissions_threads'])):
        PortBindingPermissions_t = threading.Thread(target=PortBindingPermissions, args=())
        PortBindingPermissions_t.start()
    # Start Flask server
    app.run(host='0.0.0.0', port=int(daemon_config['server']['port']))