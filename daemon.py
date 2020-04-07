import subproccess
import threading
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api')
def api():
    # TODO: Check authentication
    return jsonify({"error": {"http_code": 405}}), 405

@app.route('/api/v1'):
    return jsonify({"error": {"http_code": 405}}), 405

def QueueManager():
    # TODO: Fetch queue from the daemon DB and process it
    
def PortBindingPermissions():
    # TODO: Check binded ports' permissions

if __name__ == '__main__':
    # Define daemon threads
    QueueManager_t = threading.Thread(target=QueueManager, args=())
    PortBindingPermissions_t = threading.Thread(target=PortBindingPermissions, args=())
    # Start daemon threads
    QueueManager_t.start()
    PortBindingPermissions_t.start()
    # Start Flask server
    app.run(host='0.0.0.0', port=4070)
