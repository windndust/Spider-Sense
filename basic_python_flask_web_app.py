from flask import Flask, request, jsonify
import argparse

# -- CONFIGURATION --
LISTEN_PORT = 8080

# --- INITIALIZATION ---
app = Flask(__name__)


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "service": "Flask listener"}), 200
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A test basic python flask server')
    parser.add_argument('--port', type=int, default=LISTEN_PORT, 
        help=f'Set the port number (default: {LISTEN_PORT} )')
    args = parser.parse_args()

    print(f"Starting test basic python flask server on port {args.port}")
    app.run(host='0.0.0.0', port=args.port)