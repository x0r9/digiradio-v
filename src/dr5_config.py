"""
Handle the config for this application
"""

import os
import json

def get_config_path(config_path=None):
    """
    Search for a path that has a valid file,
    Return the path else raise IOError
    """
    result = None
    if config_path is not None:
        # Search for this file first...
        if os.path.isfile(config_path):
            result = config_path

    # If not supplied find it locally or in /etc/...
    if result is None:
        if os.path.isfile("config.json"):
            result = "config.json"
    if result is None:
        if os.path.isfile("/etc/digiradio-v/config.json"):
            result = "/etc/digiradio-v/config.json"
    if result is None:
        raise IOError("No config file found")
    return result

def get_config(config_path=None):
    p = get_config_path(config_path)
    with open(p, "r") as f:
        return json.loads(f.read())

# load config
config = get_config()

#####
## API Key things
#####

def get_api_key_setup(apikey):

    if "apikeys" not in config:
        # no keys configured
        return None

    if apikey not in config["apikeys"]:
        # The key does not exist
        return None

    # Key exists, return data
    return config["apikeys"][apikey]


