import requests
import logging
import logging.handlers
import os
import json
import mcrcon
from dotenv import load_dotenv

logger = logging.getLogger(__file__)
logging.basicConfig(filename='/opt/nebula/logs/whitelist.log', encoding='utf-8', level=logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(filename='/opt/nebula/logs/whitelist.log', mode='a', maxBytes=8000, backupCount=5, encoding='utf-8')
logger.addHandler(handler)

# Load the JSON data
try:
    with open('/opt/nebula/config.json', 'r') as file:
        data = json.load(file)
except FileNotFoundError:
    data = {}

# Error handling
if 'servers' not in data:
    data['servers'] = {}

if data:
    logger.info("[Whitelist] config.json found!")
    server_names = list(data['servers'].keys())
    for server in server_names:
        if 'access' in data['servers'][server] and data['servers'][server]['access'] == True:
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