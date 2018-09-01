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
JOURNAL_DIR = os.path.join(FILEKASTEN_DIR, "journal")

USE_NV_STYLE = False

def save_config(dirs={}, hidden=[], journal=[], export_dir="", journal_dir="", use_nv_style=False):
    pass

    yaml_obj = {}
    yaml_obj["dirs"] = dirs
    yaml_obj["hidden"] = hidden
    yaml_obj["journal"] = journal
    yaml_obj["export_dir"] = export_dir
    yaml_obj["journal_dir"] = journal_dir
    yaml_obj["use_nv_style"] = use_nv_style

    with open(FILEKASTEN_FILE, "w") as f:
        info = f.write(yaml.safe_dump(yaml_obj))

    load_config()

def load_config():
    global DIRS, JOURNAL, HIDDEN, SECRET, BACKUP_DIR, JOURNAL_DIR, USE_NV_STYLE
    if os.path.exists(FILEKASTEN_FILE):
        with open(FILEKASTEN_FILE) as f:
            info = yaml.load(f.read())

            DIRS = info.get("dirs", [])
            JOURNAL = info.get("journal", [])
            HIDDEN = info.get("hidden", [])
            SECRET = info.get("secret", "changemeplease")
            BACKUP_DIR = info.get("export_dir", BACKUP_DIR)
            JOURNAL_DIR = info.get("journal_dir", JOURNAL_DIR)
            USE_NV_STYLE = info.get("use_nv_style", USE_NV_STYLE)

load_config()
