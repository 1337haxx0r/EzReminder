from dotenv import load_dotenv
import os
from config.version import __version__

load_dotenv()

# DB config
db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}

# App config
app_config = {
    "title": os.getenv("APP_TITLE", "EzReminder"),
    "version": __version__,
    "icon": os.getenv("APP_ICON", "icon.ico"),
}
