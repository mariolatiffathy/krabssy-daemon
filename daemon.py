'''
FABITMANAGE DAEMON
@mariolatiffathy/fabitmanage-daemon
'''
import subproccess
import threading
import configparser
import time
import mysql.connector
from flask import Flask, jsonify, request

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
    check_auth_key.execute("SELECT * FROM daemon_keys WHERE key = '%s'", (auth_header))
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
                    # TODO: CREATE SERVER ACTION
    
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