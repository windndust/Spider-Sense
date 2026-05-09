from flask import Flask, request, jsonify
import argparse
import logging

# -- CONFIGURATION --
LISTEN_PORT = 8080

# --- INITIALIZATION ---
app = Flask(__name__)

def setupLog(logDirectory):
    if logDirectory.endswith("/"):
        logLocation=logDirectory+'spider-sense.log'
    else:
        logLocation=logDirectory+'/spider-sense.log'
    print(f"Log location: {logLocation}")
    logging.basicConfig(
        filename=logLocation,
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s'
    )
    logging.info("********************************")
    logging.info("************  Start ************")
    logging.info("********************************")


@app.route('/health', methods=['GET'])
def health_check():
    logging.info("Health checked")
    return jsonify({"status": "ok", "service": "Flask listener"}), 200
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A test basic python flask server')
    parser.add_argument('--port', type=int, default=LISTEN_PORT, 
        help=f'Set the port number (default: {LISTEN_PORT} )')
    parser.add_argument('--logLocation', type=str, default="./",
        help=f'Set the location for log files', required=True)
    args = parser.parse_args()

    print(f"Starting test basic python flask server on port {args.port}")
    setupLog(args.logLocation)
    app.run(host='0.0.0.0', port=args.port)