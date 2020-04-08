import subproccess
import threading
import configparser
import time
from flask import Flask, jsonify

daemon_config = configparser.ConfigParser()
daemon_config.read("/fabitmanage-daemon/config/daemon.ini")

daemondb = mysql.connector.connect(
  host=daemon_config['db']['host'],
  user=daemon_config['db']['user'],
  passwd=daemon_config['db']['password'],
  database=daemon_config['db']['name']
)

app = Flask(__name__)

@app.route('/api')
def api():
    # TODO: Check authentication
    return jsonify({"error": {"http_code": 405}}), 405

@app.route('/api/v1'):
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
    
def PortBindingPermissions():
    # TODO

if __name__ == '__main__':
    # Define daemon threads
    QueueManager_t = threading.Thread(target=QueueManager, args=())
    PortBindingPermissions_t = threading.Thread(target=PortBindingPermissions, args=())
    # Start daemon threads
    QueueManager_t.start()
    PortBindingPermissions_t.start()
    # Start Flask server
    app.run(host='0.0.0.0', port=int(daemon_config['server']['port']))