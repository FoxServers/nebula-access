import requests
import logging
import logging.handlers
import os
import json
import mcrcon
from dotenv import load_dotenv

logger = logging.getLogger(__file__)
logging.basicConfig(filename='/opt/foxservers/core/logs/whitelist.log', encoding='utf-8', level=logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(filename='/opt/foxservers/core/logs/whitelist.log', mode='a', maxBytes=8000, backupCount=5, encoding='utf-8')
logger.addHandler(handler)

json_file = open("/opt/foxservers/core/servers.json")
try:
    logger.info(f"[Whitelist] Reading servers.json config file!")
    servers_json = json.load(json_file)
except:
    logger.error(f"[Whitelist] Error attempting to read servers_json")
if servers_json:
    logger.info("[Whitelist] servers.json found!")
    for server in servers_json:
        logger.info(f"[Whitelist] Writing whitelist for {server}!")
        SERVER_DOTENV = "/srv/foxservers/" + server["server_name"] + "/.foxservers-core.env"
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
            path = "/srv/foxservers/" + SERVER_NAME + "/whitelist.json"
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
    logger.warning("[Whitelist] No servers found in servers.json file")