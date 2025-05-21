from platformdirs import user_config_dir
import os
import json

from config.version import __version__

APP_NAME = "EzReminder"
CONFIG_FILENAME = "config.json"
CONFIG_DIR = user_config_dir(APP_NAME)
CONFIG_PATH = os.path.join(CONFIG_DIR, CONFIG_FILENAME)

# Default fallback config
default_config = {
    "db": {
        "host": "localhost",
        "user": "root",
        "password": "",
        "database": "reminders"
    },
    "app": {
        "title": "EzReminder",
        "icon": "icon.ico",
        "version": __version__
    }
}

def load_user_config():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'w') as f:
            json.dump(default_config, f, indent=4)
        return default_config
    else:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)

def save_user_config(config):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=4)
