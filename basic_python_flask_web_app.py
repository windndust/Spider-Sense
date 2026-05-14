from flask import Flask, request, jsonify
import argparse
import logging
import subprocess
import time

# -- CONFIGURATION --
LISTEN_PORT = 8080
DEPLOY_SCRIPTS = "/"

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

@app.route('/deploy', methods=['POST'])
def deploy():
    logging.info("Deploy request")

    start_time = time.time()
    try:
        
        result = subprocess.run(
            ["bash" , DEPLOY_SCRIPTS+"deploy.bash"],
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        logging.info(f"Return Code: {result.returncode}, Command: {result.args}")
        logging.info(f"Script stdout: {result.stdout.strip()}")
        logging.info(f"Script stderr: {result.stderr.strip()}")
        return jsonify({"status": "ok", "message": "Deploy Success"}), 200

    except subprocess.CalledProcessError as e:
        logging.error(f"Deployment failed with return code {e.returncode}")
        logging.error(f"Command: {e.cmd}, Args: {e.args}")
        logging.error(f"Standard Error : {e.stderr}")
        logging.error(f"Standard Output: {e.stdout}")
        logging.error(f"Output: {e.output}")
        return jsonify({"status": "error", "service": "Deploy"}), 500

    except Exception as e:
        logging.exception("Unexpected exception during /deploy")
        return jsonify({"status": "error", "service": "Deploy"}), 500
        
    finally:
        duration = time.time() - start_time
        logging.info(f"Duration: {duration:.2f}s")


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
    parser.add_argument('--deployLocation', type=str, 
        help=f'Set the location for deploy screipts', required=True)
    args = parser.parse_args()

    print(f"Starting test basic python flask server on port {args.port}")
    setupLog(args.logLocation)
    DEPLOY_SCRIPTS = args.deployLocation
    app.run(host='0.0.0.0', port=args.port)