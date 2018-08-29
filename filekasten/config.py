import os
FILEKASTEN_DIR = os.path.expanduser("~/.local/share/filekasten")
if not os.path.exists(FILEKASTEN_DIR):
    os.makedirs(FILEKASTEN_DIR)

PORT = 32333

# secret key for flask session
SECRET = "changemeplease"


DIRS = []
JOURNAL = []
HIDDEN = []

import yaml
FILEKASTEN_FILE = os.path.join(FILEKASTEN_DIR, "config.yaml")

BACKUP_DIR = os.path.join(FILEKASTEN_DIR, "export")

def save_config():
    pass

def load_config():
    global DIRS, JOURNAL, HIDDEN, SECRET, BACKUP_DIR
    if os.path.exists(FILEKASTEN_FILE):
        with open(FILEKASTEN_FILE) as f:
            info = yaml.load(f.read())

            DIRS = info.get("dirs", [])
            JOURNAL = info.get("journal", [])
            HIDDEN = info.get("hidden", [])
            SECRET = info.get("secret", "changemeplease")
            BACKUP_DIR = info.get("export_dir", BACKUP_DIR)

load_config()
