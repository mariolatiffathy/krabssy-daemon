import subproccess
from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/api')
def api():
    # TODO: Check authentication
    return jsonify({})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8794)
