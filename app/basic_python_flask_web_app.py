from flask import Flask, request, jsonify
import argparse
import logging
import subprocess
import time
import os
import sys
from dotenv import load_dotenv
from typing import Dict
from typing import cast

# -- CONFIGURATION --
LISTEN_PORT = 8080
DEPLOY_SCRIPTS = "/"
CRED_DICT: Dict[str, str] = {}
CONFIG_LOCATION={"1": ""}

# --- INITIALIZATION ---
app = Flask(__name__)

def setupLog(logDirectory):
    if not logDirectory.endswith("/"):
        logDirectory=logDirectory+'/'

    format = '%(asctime)s %(name)s %(levelname)s %(message)s'
    log_format = logging.Formatter(format)

    logging.basicConfig(
        filename=logDirectory+"spider-sense-module.log",
        level=logging.INFO,
        format=format        
    )

    fileHandler = logging.FileHandler(logDirectory+"spider-sense.log")
    fileHandler.setFormatter(log_format)

    stdHandler = logging.StreamHandler(sys.stdout)
    stdHandler.setFormatter(log_format)

    spiderSenseStart = logging.getLogger("spider-sense-start")
    spiderSenseStart.setLevel(logging.INFO)
    spiderSenseStart.addHandler(fileHandler)
    spiderSenseStart.addHandler(stdHandler)
    spiderSenseStart.propagate = False

    spiderSense = logging.getLogger("spider-sense")
    spiderSense.setLevel(logging.INFO)
    spiderSense.addHandler(fileHandler)
    spiderSense.propagate = False

    spiderSenseStart.info(f"*** Module Log Location ${logDirectory}spider-sense-module.log")
    spiderSenseStart.info(f"*** App Log Location ${logDirectory}spider-sense.log")
    return spiderSenseStart

def load_secrets():
    spiderSenseStart = logging.getLogger("spider-sense-start")
    secrets_path = os.path.join(os.getcwd(), "secrets.env")

    if os.path.exists(secrets_path):
        load_dotenv(dotenv_path=secrets_path)
        spiderSenseStart.info("secrets.env Found")
    else:
        spiderSenseStart.error("secrets.env not Found")
        exit(1)

    gh_cred_map = os.environ.get("GH_CRED_MAP", "")
    if not gh_cred_map:
        spiderSenseStart.error("GH_CRED_MAP variable not found in secrets.env. This variable maps github login to personal access token. Format - githubLogin:PAT;githubLogin2:PAT2;")
        exit(1)
    CRED_DICT.update(dict(item.split(":") for item in gh_cred_map.split(";") if ":" in item))

    configLocation = os.environ.get("CONFIG_LOCATION", "")
    if not configLocation:
        spiderSenseStart.error("CONFIG_LOCATION variable not found in secrets.env. This variable represents a directory of a config file to mount to the container filesystem")
    CONFIG_LOCATION["1"]=configLocation



@app.route('/deploy', methods=['POST'])
def deploy():
    spiderSense = logging.getLogger("spider-sense")
    spiderSense.info("/deploy requested")

    data = request.get_json()
    spiderSense.info(f"Json body:\n{data}")

    package = data.get("package", {})
    name = package.get("name", {})
    packageVersion = package.get("package_version", {})
    login = packageVersion.get("author", {}).get("login", {})
    package_url = packageVersion.get("package_url", {})
    spiderSense.info(f"url {package_url}")

    gh_pat = CRED_DICT.get(login)
    if not gh_pat:
        return jsonify({"status": "error", "message": "Unknown github login"}), 400

    start_time = time.time()
    try:
        script_path = os.path.join(DEPLOY_SCRIPTS, "deploy.bash")

        spiderSense.info(f"Checking script existence: {os.path.exists(script_path)}")
        spiderSense.info(f"Checking script permissions (readable): {os.access(script_path, os.R_OK)}")
        spiderSense.info(f"Checking script permissions (executable): {os.access(script_path, os.X_OK)}")
        result = subprocess.run(
            ["sudo", 
            f"GH_USER="+cast(str, login), 
            f"GH_PAT={gh_pat}", 
            f"GH_URL="+cast(str, package_url),
            f"GH_NAME="+cast(str, name),
            f"CONFIG_LOCATION={CONFIG_LOCATION['1']}",
            script_path],
            shell=True,
            capture_output=True,
            text=True,
            check=True,
            timeout=60
        )
        spiderSense.info(f"Return Code: {result.returncode}, Command: {result.args}")
        spiderSense.info(f"Script stdout:\n{result.stdout.strip()}")
        spiderSense.info(f"Script stderr:\n{result.stderr.strip()}")
        return jsonify({"status": "ok", "message": "Deploy Success"}), 200

    except subprocess.CalledProcessError as e:
        spiderSense.error(f"Deployment failed with return code {e.returncode}")
        spiderSense.error(f"Command: {e.cmd}, Args: {e.args}")
        spiderSense.error(f"Standard Error :\n{e.stderr}")
        spiderSense.error(f"Standard Output:\n{e.stdout}")
        spiderSense.error(f"Output: {e.output}")
        return jsonify({"status": "error", "service": "Deploy"}), 500

    except Exception as e:
        spiderSense.exception("Unexpected exception during /deploy")
        return jsonify({"status": "error", "service": "Deploy"}), 500
        
    finally:
        duration = time.time() - start_time
        spiderSense.info(f"Duration: {duration:.2f}s")


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
        help=f'Set the location for deploy scripts', required=True)
    args = parser.parse_args()

    spiderSenseStart = setupLog(args.logLocation)    
    load_secrets()
    DEPLOY_SCRIPTS = args.deployLocation
    spiderSenseStart.info(f"Starting python flask server on port {args.port}")
    app.run(host='0.0.0.0', port=args.port)