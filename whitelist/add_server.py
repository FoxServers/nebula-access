import logging
import logging.handlers
import sys
import json

logger = logging.getLogger(__file__)
logging.basicConfig(filename='/opt/nebula/logs/access.log', encoding='utf-8', level=logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(filename='/opt/nebula/logs/access.log', mode='a', maxBytes=8000, backupCount=3, encoding='utf-8')
logger.addHandler(handler)

if (len(sys.argv) < 2):
    logger.error(f"[Server Manager] Failed to add server: Missing server name")
    raise ValueError("[Server Manager] Failed to add server: Missing server name")

def save_data(data):
    # Save the changes
    with open('/opt/nebula/config.json', 'w') as file:
        json.dump(data, file, indent=4)

def add_server(server_name, data, logger):
    server_data = {
        "access": True
    }
    data['servers'][server_name] = server_data
    logger.info(f"[Server Manager] Added {server_name} to access")
    save_data(data)

def update_server(server_name, data, logger):
    data['servers'][server_name]['access'] = True
    logger.info(f"[Server Manager] Updated {server_name} access to True")
    save_data(data)

try:
    # Load the JSON data
    try:
        with open('/opt/nebula/config.json', 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}

    # Error handling
    if 'servers' not in data:
        data['servers'] = {}

    # Extract server names
    server_names = list(data.get('servers', {}).keys())
    if sys.argv[1] not in data['servers']:
        add_server(server_name=sys.argv[1], data=data, logger=logger)
    else:
        update_server(server_name=sys.argv[1], data=data, logger=logger)

except Exception as e:
    logger.error(f"[Server Manager] A critical error has occurred: {e}")