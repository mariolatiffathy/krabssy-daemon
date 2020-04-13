# -*- coding: utf-8 -*-
'''
FABITMANAGE DAEMON
@mariolatiffathy/fabitmanage-daemon
'''
import subprocess
import threading
import configparser
import time
import json
import uuid
import crypt
import os
import platform
import sys
import random
import string
import mysql.connector
import atexit
from flask import Flask, jsonify, request
from waitress import serve
from pyftpdlib.authorizers import DummyAuthorizer 
from pyftpdlib.handlers import FTPHandler 
from pyftpdlib.servers import FTPServer
from socket import *
from psutil import process_iter

# Logger
def Logger(type, message):
    if type == "error":
        TYPE_TAG = "[ERROR]"
    if type == "warn":
        TYPE_TAG = "[WARNING]"
    if type == "info":
        TYPE_TAG = "[INFORMATION]"
    print("[DAEMON] " + TYPE_TAG + " " + message)
    
# Functions
def get_size(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path): 
        for f in filenames: 
            fp = os.path.join(dirpath, f) 
            # skip if it is symbolic link 
            if not os.path.islink(fp): 
                total_size += os.path.getsize(fp) 
    return total_size

# Load daemon configuration file
daemon_config = configparser.ConfigParser()
daemon_config.read("/fabitmanage-daemon/config/daemon.ini")
    
# Variables
daemon_version = "v0.1-alpha"

# Fixed responses
RES_UNAUTHENTICATED = {"error": {"http_code": 403}}

# Define the daemon DB settings. This dict will be passed as kwargs
# ... More explaination: https://www.geeksforgeeks.org/python-passing-dictionary-as-keyword-arguments/?ref=rp
# ... or see https://www.geeksforgeeks.org/connect-mysql-database-using-mysql-connector-python/ "Another way is to pass the dictionary in the connect() function using ‘**’ operator:" section.
db_settings = {
    "host": daemon_config['db']['host'],
    "user": daemon_config['db']['user'],
    "passwd": daemon_config['db']['password'],
    "database": daemon_config['db']['name']
}

# Define the daemon FTP server authorizer globally
ftp_authorizer = DummyAuthorizer()

# Init Flask app
app = Flask(__name__)

def IS_AUTHENTICATED(auth_header):
    daemondb = mysql.connector.connect(**db_settings)
    check_auth_key = daemondb.cursor(dictionary=True)
    check_auth_key.execute("SELECT * FROM daemon_keys WHERE d_key = %s", (auth_header,))
    check_auth_key.fetchall()
    if check_auth_key.rowcount == 0:
        daemondb.close()
        return False
    else:
        daemondb.close()
        return True

@app.route('/api')
def api():
    if request.headers.get('Authorization') is not None:
        if IS_AUTHENTICATED(request.headers.get('Authorization')) == False:
            return jsonify(RES_UNAUTHENTICATED), 403
    else:
        return jsonify(RES_UNAUTHENTICATED), 403
    return jsonify({"error": {"http_code": 405}}), 405

@app.route('/api/v1')
def api_v1():
    if request.headers.get('Authorization') is not None:
        if IS_AUTHENTICATED(request.headers.get('Authorization')) == False:
            return jsonify(RES_UNAUTHENTICATED), 403
    else:
        return jsonify(RES_UNAUTHENTICATED), 403
    return jsonify({"error": {"http_code": 405}}), 405
    
@app.route('/api/v1/servers/create', methods=['POST'])
def create_server():
    if request.headers.get('Authorization') is not None:
        if IS_AUTHENTICATED(request.headers.get('Authorization')) == False:
            return jsonify(RES_UNAUTHENTICATED), 403
    else:
        return jsonify(RES_UNAUTHENTICATED), 403
    daemondb = mysql.connector.connect(**db_settings)
    req_data = request.get_json()
    required_data = ["allowed_ports", "server_id", "enable_ftp", "ram", "cpu", "disk", "startup_command", "fabitimage_id"]
    for required in required_data:
        if not required in req_data:
            return jsonify({"error": {"http_code": 422, "description": "You are missing a required field."}}), 422
    if "," in req_data['allowed_ports']:
        ports = req_data['allowed_ports'].split(',')
        for port in ports:
            if int(port) > 65535 or int(port) == 0:
                return jsonify({"error": {"http_code": 422, "description": "The port " + str(port) + " is not a 16-bit port."}}), 422
    else:
        if int(req_data['allowed_ports']) > 65535 or int(req_data['allowed_ports']) == 0:
            return jsonify({"error": {"http_code": 422, "description": "The port " + str(req_data['allowed_ports']) + " is not a 16-bit port."}}), 422
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
    check_serverid_exists = daemondb.cursor(dictionary=True)
    check_serverid_exists.execute("SELECT * FROM servers WHERE server_id = %s", (req_data['server_id'],))
    check_serverid_exists.fetchall()
    if check_serverid_exists.rowcount >= 1:
        return jsonify({"error": {"http_code": 422, "description": "Another server with this server_id already exists."}}), 422
    check_fabitimage_exists = daemondb.cursor(dictionary=True)
    check_fabitimage_exists.execute("SELECT * FROM images WHERE id = %s", (int(req_data['fabitimage_id']),))
    check_fabitimage_exists.fetchall()
    if check_fabitimage_exists.rowcount == 0:
        return jsonify({"error": {"http_code": 404, "description": "The inputted fabitimage_id doesn't exists."}}), 404
    queue_parameters = json.dumps(req_data)
    queue_action = "create_server"
    queuepush = daemondb.cursor(dictionary=True)
    queuepush.execute("INSERT INTO queue (action, parameters, being_processed) VALUES (%s, %s, %s)", (queue_action, queue_parameters, 0,))
    daemondb.commit()
    daemondb.close()
    return jsonify({"success": {"http_code": 200, "description": "Server successfully queued for creation."}}), 200
    
@app.route('/api/v1/servers/<server_id>', methods=['GET', 'DELETE'])
def server(server_id):
    if request.headers.get('Authorization') is not None:
        if IS_AUTHENTICATED(request.headers.get('Authorization')) == False:
            return jsonify(RES_UNAUTHENTICATED), 403
    else:
        return jsonify(RES_UNAUTHENTICATED), 403
    if not server_id or server_id == "":
        return jsonify({"error": {"http_code": 422, "description": "You are missing a required field."}}), 422
    daemondb = mysql.connector.connect(**db_settings)
    check_serverid_exists = daemondb.cursor(dictionary=True)
    check_serverid_exists.execute("SELECT * FROM servers WHERE server_id = %s", (server_id,))
    check_serverid_exists.fetchall()
    if check_serverid_exists.rowcount == 0:
        return jsonify({"error": {"http_code": 404, "description": "This server doesn't exists."}}), 404
    # METHOD/DELETE
    if request.method == 'DELETE':
        queue_parameters = json.dumps({"server_id": server_id})
        queue_action = "delete_server"
        queuepush = daemondb.cursor(dictionary=True)
        queuepush.execute("INSERT INTO queue (action, parameters, being_processed) VALUES (%s, %s, %s)", (queue_action, queue_parameters, 0,))
        daemondb.commit()
        return jsonify({"success": {"http_code": 200, "description": "Server successfully queued for deletion."}}), 200
    # METHOD/GET
    if request.method == 'GET':
        IS_SERVER_ONLINE = False
        SERVER_CONTAINER_ID = ""
        SERVER_FABITIMAGE_ID = 0
        SERVER_ALLOWED_PORTS = ""
        SERVER_STARTUP_COMMAND = ""
        SERVER_FTP_ENABLED = False
        SERVER_FTP_USERNAME = ""
        SERVER_FTP_PASSWORD = ""
        SERVER_USED_MEMORY = 0
        SERVER_TOTAL_MEMORY = 0
        SERVER_USED_DISK = 0
        SERVER_TOTAL_DISK = 0
        SERVER_USED_CPU = 0
        SERVER_TOTAL_CPU = 0
        get_server = daemondb.cursor(dictionary=True)
        get_server.execute("SELECT * FROM servers WHERE server_id = %s", (server_id,))
        get_server_result = get_server.fetchall()
        if get_server.rowcount > 0:
            for server in get_server_result:
                SERVER_CONTAINER_ID = server['container_id']
                SERVER_FABITIMAGE_ID = server['fabitimage_id']
                SERVER_STARTUP_COMMAND = server['startup_command']
                SERVER_TOTAL_MEMORY = server['ram']
                SERVER_TOTAL_DISK = server['disk']
                SERVER_TOTAL_CPU = server['cpu']
                if server['enable_ftp'] == 1:
                    SERVER_FTP_ENABLED = True
                    SERVER_FTP_USERNAME = server['ftp_username']
                    SERVER_FTP_PASSWORD = server['ftp_password']
                if "," in server['allowed_ports']:
                    SERVER_ALLOWED_PORTS = server['allowed_ports'].split(',')
                else:
                    SERVER_ALLOWED_PORTS = server['allowed_ports']
        for proc in process_iter():
            if proc.username() == SERVER_CONTAINER_ID and proc.name() != "sh" and proc.name() != "bash":
                IS_SERVER_ONLINE = True
                MEM_INFO = proc.memory_info()
                USED_PHYSICAL = MEM_INFO.rss / 1000000
                SERVER_USED_MEMORY = SERVER_USED_MEMORY + USED_PHYSICAL
                SERVER_USED_CPU = SERVER_USED_CPU + proc.cpu_percent()
        SERVER_USED_DISK = get_size('/home/fabitmanage/daemon-data/' + SERVER_CONTAINER_ID) / 1000000
        return jsonify({"success": {"http_code": 200, "description": ""}, "server": {"is_online": IS_SERVER_ONLINE, "container_id": SERVER_CONTAINER_ID, "fabitimage_id": SERVER_FABITIMAGE_ID, "allowed_ports": SERVER_ALLOWED_PORTS, "startup_command": SERVER_STARTUP_COMMAND, "ftp_enabled": SERVER_FTP_ENABLED, "ftp_username": SERVER_FTP_USERNAME, "ftp_password": SERVER_FTP_PASSWORD, "used_memory": SERVER_USED_MEMORY, "total_memory": SERVER_TOTAL_MEMORY, "used_disk": SERVER_USED_DISK, "total_disk": SERVER_TOTAL_DISK, "used_cpu": SERVER_USED_CPU, "total_cpu": SERVER_TOTAL_CPU}}), 200
    daemondb.close()
    
# Flask Custom Errors
@app.errorhandler(404)
def daemon_err_404(e):
    return jsonify({"error": {"http_code": 404}}), 404
app.register_error_handler(404, daemon_err_404)

@app.errorhandler(405)
def daemon_err_405(e):
    return jsonify({"error": {"http_code": 405}}), 405
app.register_error_handler(405, daemon_err_405)

@app.errorhandler(500)
def daemon_err_500(e):
    return jsonify({"error": {"http_code": 500}}), 500
app.register_error_handler(500, daemon_err_500)
    
def AsUser(uid, gid):
    def set_ids():
        os.setgid(gid)
        os.setuid(uid)
    return set_ids
    
def QueueManager():
    while True:
        time.sleep(random.randint(100, 501)/100)
        global ftp_authorizer
        daemondb = mysql.connector.connect(**db_settings)
        queue_cursor = daemondb.cursor(dictionary=True)
        queue_cursor.execute("SELECT * FROM queue WHERE being_processed = 0")
        result = queue_cursor.fetchone()
        if queue_cursor.rowcount > 0:
           update_being_processed = daemondb.cursor(dictionary=True)
           update_being_processed.execute("UPDATE queue SET being_processed = 1 WHERE id = %s", (result['id'],))
           daemondb.commit()
           
           queue_action = result['action']
           queue_parameters = json.loads(result['parameters'])
           
           if queue_action == "create_server":
               # Define container ID
               CONTAINER_ID = "fabitmanage-" + str(uuid.uuid4()).replace("-", "")[0:15] # Note: Must meet the Linux username rules https://stackoverflow.com/a/6949914/8524395
               # Create the container
               subprocess.check_output(['mkdir', '-p', '/home/fabitmanage/daemon-data/' + CONTAINER_ID])
               subprocess.check_output(["useradd", "-m", "-d", "/home/fabitmanage/daemon-data/" + CONTAINER_ID, "-p", crypt.crypt(str(uuid.uuid4()) + str(uuid.uuid4())), CONTAINER_ID])
               # Give the user access to his container directory
               subprocess.check_output(['chown', '-R', CONTAINER_ID + ":" + CONTAINER_ID, '/home/fabitmanage/daemon-data/' + CONTAINER_ID + '/'])
               # Define the cgconfig kernel configuration
               CGCONFIG_KERNEL_CFG = "group " + CONTAINER_ID + " { cpu { cpu.shares = " + str(int(queue_parameters['cpu'])) + "; } memory { memory.limit_in_bytes = " + str(int(queue_parameters['ram'])) + "m; memory.memsw.limit_in_bytes = " + str(int(queue_parameters['ram'])) + "m; } }"
               # Get the filesystem of the partition /home
               FSCK = subprocess.check_output(['fsck', '-N', '/home'])
               filesystem = FSCK.decode().splitlines()[1].split(" ")[5].rstrip()
               # Set disk quota for the container
               subprocess.check_output(["setquota", CONTAINER_ID, str(int(queue_parameters['disk'])*1000), str(int(queue_parameters['disk'])*1000), "0", "0", filesystem])
               # Write kernel configurations
               push_cgconfig = daemondb.cursor(dictionary=True)
               push_cgconfig.execute("INSERT INTO cgroups_files (file, line) VALUES (%s, %s)", ("cgconfig", CGCONFIG_KERNEL_CFG,))
               daemondb.commit()
               push_cgrules = daemondb.cursor(dictionary=True)
               push_cgrules.execute("INSERT INTO cgroups_files (file, line) VALUES (%s, %s)", ("cgrules", CONTAINER_ID + " memory,cpu " + CONTAINER_ID,))
               daemondb.commit()
               # Get the FabitImage
               FABITIMAGE_PATH = ""
               FABITIMAGE_JSON = ""
               get_fabitimage = daemondb.cursor(dictionary=True)
               get_fabitimage.execute("SELECT * FROM images WHERE id = %s", (int(queue_parameters['fabitimage_id']),))
               get_fabitimage_result = get_fabitimage.fetchall()
               if get_fabitimage.rowcount > 0:
                   for image in get_fabitimage_result:
                       FABITIMAGE_PATH = image['path']
               with open(FABITIMAGE_PATH, "r") as FABITIMAGE_FILE:
                   FABITIMAGE_JSON = FABITIMAGE_FILE.read()
               FABITIMAGE_PARSED = json.loads(FABITIMAGE_JSON)
               # Get the container UID and GID
               CONTAINER_UID = subprocess.check_output(['id', '-u', CONTAINER_ID]).decode().rstrip()
               CONTAINER_GID = subprocess.check_output(['id', '-g', CONTAINER_ID]).decode().rstrip()
               # FABITIMAGE/PROCESS_EVENT on_create
               if "from_container" in FABITIMAGE_PARSED['events']['on_create']:
                   for command in FABITIMAGE_PARSED['events']['on_create']['from_container']:
                       cmd = FABITIMAGE_PARSED['events']['on_create']['from_container'][command]
                       try:
                           subprocess.check_output(cmd.split(" "), preexec_fn=AsUser(int(CONTAINER_UID), int(CONTAINER_GID)), cwd="/home/fabitmanage/daemon-data/" + CONTAINER_ID)
                       except Exception as e:
                           Logger("warn", "Failed to execute command '" + cmd + "' from container on server creation.")
               if "as_root" in FABITIMAGE_PARSED['events']['on_create']:
                   for command in FABITIMAGE_PARSED['events']['on_create']['as_root']:
                       cmd = FABITIMAGE_PARSED['events']['on_create']['as_root'][command]
                       try:
                           subprocess.check_output(cmd.split(" "), cwd="/home/fabitmanage/daemon-data/" + CONTAINER_ID)
                       except Exception as e:
                           Logger("warn", "Failed to execute command '" + cmd + "' as root on server creation.")
               if queue_parameters['enable_ftp'] == True:
                   enable_ftp = 1
                   ftp_username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
                   ftp_password = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=16))
                   ftp_authorizer.add_user(ftp_username, ftp_password, "/home/fabitmanage/daemon-data/" + CONTAINER_ID, perm="elradfmwMT")
               else:
                   enable_ftp = 0
                   ftp_username = ""
                   ftp_password = ""
               push_server = daemondb.cursor(dictionary=True)
               push_server.execute("INSERT INTO servers (server_id, container_id, container_uid, container_gid, fabitimage_id, startup_command, enable_ftp, ftp_username, ftp_password, allowed_ports, disk, cpu, ram) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (str(queue_parameters['server_id']), str(CONTAINER_ID), int(CONTAINER_UID), int(CONTAINER_GID), int(queue_parameters['fabitimage_id']), str(queue_parameters['startup_command']), enable_ftp, ftp_username, ftp_password, queue_parameters['allowed_ports'], int(queue_parameters['disk']), int(queue_parameters['cpu']), int(queue_parameters['ram']),))
               daemondb.commit()
               Logger("info", "Created server with container ID " + CONTAINER_ID)
                   
           if queue_action == "delete_server":
               CONTAINER_ID = ""
               IS_FTP_ENABLED = False
               FTP_USERNAME = ""
               get_server = daemondb.cursor(dictionary=True)
               get_server.execute("SELECT * FROM servers WHERE server_id = %s", (queue_parameters['server_id'],))
               get_server_result = get_server.fetchall()
               if get_server.rowcount > 0:
                   for server in get_server_result:
                       CONTAINER_ID = server['container_id']
                       if server['enable_ftp'] == 1:
                           IS_FTP_ENABLED = True
                           FTP_USERNAME = server['ftp_username']
               # Kill the container if running
               try:
                   subprocess.check_output(['screen', '-S', CONTAINER_ID, '-X', 'quit'])
               except Exception as e:
                   pass
               # Force delete the container with its daemon-data directory
               try:
                   subprocess.check_output(['userdel', '-r', '-f', CONTAINER_ID])
               except Exception as e:
                   pass
               # Delete the cgroups kernel configurations and rules of the container
               delete_cgroups = daemondb.cursor(dictionary=True)
               delete_cgroups.execute("DELETE FROM cgroups_files WHERE line LIKE '%%%s%%'", (CONTAINER_ID,))
               daemondb.commit()
               # Make sure the daemon-data directory of the container was deleted
               try:
                   subprocess.check_output(['rm', '-rf', "/home/fabitmanage/daemon-data/" + CONTAINER_ID])
               except Exception as e:
                   pass
               # Remove the container's FTP if enabled
               if IS_FTP_ENABLED == True:
                   ftp_authorizer.remove_user(FTP_USERNAME)
               # Remove the server from the daemon DB
               delete_server = daemondb.cursor(dictionary=True)
               delete_server.execute("DELETE FROM servers WHERE server_id = %s", (queue_parameters['server_id'],))
               daemondb.commit()
               Logger("info", "Deleted server with container ID " + CONTAINER_ID)
               
           delete_queue = daemondb.cursor(dictionary=True)
           delete_queue.execute("DELETE FROM queue WHERE id = %s", (result['id'],))
           daemondb.commit()
           daemondb.close()
    
def PortBindingPermissions():
    # Thanks to https://stackoverflow.com/a/37968428/8524395
    # Thanks to https://stackoverflow.com/a/20691431/8524395
    while True:
        time.sleep(random.randint(100, 501)/100)
        port = 0
        while port <= 65535:
            try:
                try:
                    socket_s = socket(AF_INET, SOCK_STREAM, 0)
                except:
                    break
                socket_s.connect(("0.0.0.0", port))
                connected = True
            except ConnectionRefusedError:
                connected = False
            finally:
                if(connected and port != socket_s.getsockname()[1]):
                    pid = 0
                    pid_owner = ""
                    for proc in process_iter():
                        try:
                            for conns in proc.connections(kind='all'):
                                if conns.laddr.port == int(port):
                                    pid = int(proc.pid)
                                    pid_owner = proc.username()
                        except Exception as e:
                            pass
                    if "fabitmanage-" in pid_owner:
                        # The process is owned by a daemon container... Now check if the container has permissions to bind on this port.
                        daemondb = mysql.connector.connect(**db_settings)
                        get_server = daemondb.cursor(dictionary=True)
                        get_server.execute("SELECT * FROM servers WHERE container_id = %s", (pid_owner,))
                        get_server_result = get_server.fetchall()
                        if get_server.rowcount > 0:
                            for server in get_server_result:
                                if not str(port) in server['allowed_ports']:
                                    try:
                                        subprocess.check_output(["kill", "-9", str(pid)])
                                        Logger("info", "Terminated container " + pid_owner + ":" + str(pid) + " for listening on an disallowed port " + str(port))
                                    except Exception as e:
                                        pass
                        daemondb.close()
                port = port + 1
                socket_s.close()
        
def cgroups_refresher():
    while True:
        if not os.path.exists('/etc/cgconfig.conf'):
            with open('/etc/cgconfig.conf', 'w'): pass
        if 'ubuntu' in platform.platform().lower() or 'debian' in platform.platform().lower():
            subprocess.check_output(['cgconfigparser', '-l', '/etc/cgconfig.conf'])
            try:
                subprocess.check_output(['killall', 'cgrulesengd'])
            except Exception as e:
                pass
            subprocess.check_output(['cgrulesengd'])
        else:
            subprocess.check_output(['service', 'cgred', 'restart'])
            subprocess.check_output(['service', 'cgconfig', 'restart'])
        time.sleep(int(daemon_config['cgroups']['refresher_interval']))
        
def cgroups_writer():
    while True:
        cgconfig = ""
        cgrules = ""
        daemondb = mysql.connector.connect(**db_settings)
        get_lines = daemondb.cursor(dictionary=True)
        get_lines.execute("SELECT * FROM cgroups_files")
        get_lines_result = get_lines.fetchall()
        if get_lines.rowcount > 0:
            for line in get_lines_result:
                if line['file'] == "cgconfig":
                    cgconfig = cgconfig + line['line'] + "\n"
                if line['file'] == "cgrules":
                    cgrules = cgrules + line['line'] + "\n"
        daemondb.close()
        with open('/etc/cgconfig.conf', 'w+') as cgconfig_f: 
            cgconfig_f.write(cgconfig)
        with open('/etc/cgrules.conf', 'w+') as cgrules_f: 
            cgrules_f.write(cgrules)
        time.sleep(int(daemon_config['cgroups']['writer_interval']))
        
def daemon_FTP():
    global ftp_authorizer
    handler = FTPHandler
    handler.authorizer = ftp_authorizer
    ftpserv = FTPServer(("0.0.0.0", int(daemon_config['ftp_server']['port'])), handler)
    daemondb = mysql.connector.connect(**db_settings)
    get_servers = daemondb.cursor(dictionary=True)
    get_servers.execute("SELECT * FROM servers WHERE enable_ftp = 1")
    get_servers_result = get_servers.fetchall()
    if get_servers.rowcount > 0:
        for server in get_servers_result:
            ftp_authorizer.add_user(server['ftp_username'], server['ftp_password'], "/home/fabitmanage/daemon-data/" + server['container_id'], perm="elradfmwMT")
    daemondb.close()
    ftpserv.serve_forever()
    
def exit_handler():
    print("Exiting FabitManage daemon...")
    if 'ubuntu' in platform.platform().lower() or 'debian' in platform.platform().lower():
        try:
            subprocess.check_output(['killall', 'cgrulesengd'])
        except Exception as e:
            pass
    try:
        subprocess.check_output(['killall', 'screen'])
    except Exception as e:
        pass
    sys.exit()

if __name__ == '__main__':
    atexit.register(exit_handler)
    print("FabitManage Daemon " + daemon_version)
    print("Starting threads & components...")
    # Test the connection to the daemon DB
    try:
        daemondb_connection_test = mysql.connector.connect(
        **db_settings
       )
    except mysql.connector.errors.DatabaseError as e:
        Logger("error", "Unable to connect to the daemon database.")
        sys.exit()
    # Define & start the daemon threads
    for _ in range(int(daemon_config['threads']['queuemanager_threads'])):
        QueueManager_t = threading.Thread(target=QueueManager, args=())
        QueueManager_t.start()
    PortBindingPermissions_t = threading.Thread(target=PortBindingPermissions, args=())
    PortBindingPermissions_t.start()
    cgroups_refresher_t = threading.Thread(target=cgroups_refresher, args=())
    cgroups_refresher_t.start()
    cgroups_writer_t = threading.Thread(target=cgroups_writer, args=())
    cgroups_writer_t.start()
    daemon_ftp_t = threading.Thread(target=daemon_FTP, args=())
    daemon_ftp_t.start()
    # Start Flask server
    serve(app, host="0.0.0.0", port=int(daemon_config['server']['port']))