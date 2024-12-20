import requests
import logging
import logging.handlers
import os
import json
import mcrcon
import redis
from dotenv import load_dotenv

logger = logging.getLogger(__file__)
logging.basicConfig(filename='/opt/nebula/logs/whitelist.log', encoding='utf-8', level=logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(filename='/opt/nebula/logs/whitelist.log', mode='a', maxBytes=8000, backupCount=5, encoding='utf-8')
logger.addHandler(handler)

# Load the JSON data
try:
    with open('/opt/nebula/config.json', 'r') as file:
        config = json.load(file)
except FileNotFoundError:
    config = {}

# Parse config for redis
redis_config = config.get("redis")
servers = config.get("servers")
file_paths = []
for server in servers:
    file_paths.append(f"/srv/nebula/{server}/logs/latest.log")
logger.debug(f"Found logreader configs in config.json: {redis_config, file_paths}")
if redis_config:
    host = redis_config.get("ip", "localhost")
    port = redis_config.get("port", 6379)
else:
    host = "localhost"
    port = 6379
logger.debug(f"Communicating with redis at: {host, port}")

# Connect to Redis
try:
    r = redis.StrictRedis(host=host, port=port, db=0)
except redis.ConnectionError as e:
    logger.critical(f"Failed to connect to Redis: {e}")
    raise SystemExit("Critical error: Unable to connect to Redis.")

# Name of the channel
channel = 'connection_logs'

# Subscribe to the channel
pubsub = r.pubsub()
pubsub.subscribe(channel)
logger.info(f"Subscribed to {channel}. Waiting for messages...")

# Error handling
if 'servers' not in config:
    config['servers'] = {}

# Continuously listen for messages
for message in pubsub.listen():
    connection = False
    # Receive message
    if message['type'] == 'message':
        logger.info(f"Received message: {message['data'].decode('utf-8')}")
        # If a new message comes through on connection_log channel, set connection to True
        connection = True

    # If config is set up and message is a connection, get new whitelist
    if config and connection:
        logger.info("[Whitelist] config.json found!")
        server_names = list(config['servers'].keys())
        for server in server_names:
            if 'access' in config['servers'][server] and config['servers'][server]['access'] == True:
                logger.info(f"[Whitelist] Writing whitelist for {server}!")
                SERVER_DOTENV = "/srv/nebula/" + server + "/.nebula.env"
                load_dotenv(dotenv_path=SERVER_DOTENV, override=True)
                SERVER_NAME = os.getenv('SERVER_NAME')
                API_TOKEN = os.getenv('API_TOKEN')
                GAME = os.getenv('GAME')
                WHITELIST = os.getenv('WHITELIST')
                OUTPUT_PATH = os.getenv('WHITELIST_PATH')
                WHITELIST_URL = os.getenv('WHITELIST_URL')
                PASSWORD = os.getenv('RCON_PASSWORD')
                SERVER_PORT = os.getenv('SERVER_PORT')

                headers =  {'Api-Token':API_TOKEN,
                            'Game':GAME,
                            'Whitelist':WHITELIST}

                rcon = mcrcon.MCRcon("127.0.0.1", PASSWORD)
                rcon.port = int(SERVER_PORT + '1')
                response = requests.get(url=WHITELIST_URL,headers=headers)
                if(response.status_code == 401):
                    logger.error(f"[Whitelist] Error authenticating request for {server}, please ensure token is correct: {response}")
                    ConnectionRefusedError(f"[Whitelist] Error authenticating request for {server}, please ensure token is correct: {response}")
                    quit()
                if(response.status_code == 400):
                    logger.error("[Whitelist] Error, whitelist could not be found")
                    ConnectionError("[Whitelist] Error, whitelist could not be found")
                    quit()
                if(response.status_code == 200):
                    logger.info("[Whitelist] Connection Success!")
                content = response.text

                if(OUTPUT_PATH):
                    path = OUTPUT_PATH
                else:
                    path = "/srv/nebula/" + SERVER_NAME + "/whitelist.json"
                logger.info(f"[Whitelist] Attempting to update {path}")

                try:
                    FILE = open(path, "r")
                    filecontents = FILE.read()
                    FILE.close()
                    if(filecontents != content):
                        logger.info("[Whitelist] Updating whitelist...")
                        FILE = open(path, "w")  
                        FILE.write(content)
                        FILE.close()
                        logger.info("[Whitelist] Reloading whitelist...")
                        try:
                            rcon.connect()
                            response = rcon.command("/whitelist reload")
                            logger.info(response)
                            rcon.disconnect()
                        except:
                            logger.warning("[Whitelist] Error connecting to RCON, whitelist must be reloaded manually")
                    else:
                        logger.info("[Whitelist] Whitelist is already up to date")
                except:
                    logger.warning("[Whitelist] Whitelist file is missing, recreating...")
                    FILE = open(path, "w")  
                    FILE.write(content)
                    FILE.close()
                    try:
                        logger.info("[Whitelist] Reloading whitelist...")
                        rcon.connect()
                        response = rcon.command("/whitelist reload")
                        logger.info(f"[Whitelist] {response}")
                        rcon.disconnect()
                    except:
                        logger.warning("[Whitelist] Error connecting to RCON, whitelist must be reloaded manually")
    else:
        logger.warning("[Whitelist] No servers found in config.json file")