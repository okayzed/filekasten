import os
import addict
import yaml

PROFILE=os.environ.get("PROFILE", "default")
FILEKASTEN_DIR = os.path.expanduser("~/.local/share/filekasten/%s" % (PROFILE))
FILEKASTEN_FILE = os.path.join(FILEKASTEN_DIR, "config.yaml.new")
if not os.path.exists(FILEKASTEN_DIR):
    os.makedirs(FILEKASTEN_DIR)

opts = addict.Dict()

STRING_KEYS = {}
LIST_KEYS = {}


def add_config_string(prop, default=None, name=None):
    STRING_KEYS[prop] = prop
    opts[prop] = default

def add_config_string_list(prop, default=[], name=None):
    LIST_KEYS[prop] = prop
    opts[prop] = default


def update(args):
    for arg in args:
        set(arg, args[arg])

def save_config():
#    print "SAVING CONFIG", opts.toDict()
    with open(FILEKASTEN_FILE, "w") as f:
        info = f.write(yaml.safe_dump(opts.to_dict(), default_flow_style=False))

    read_config()

def read_config():
    if os.path.exists(FILEKASTEN_FILE):
        with open(FILEKASTEN_FILE) as f:
            info = yaml.load(f.read())

        if not info:
            return

        for key in info:
            if key in STRING_KEYS:
                prop = STRING_KEYS[key]
                opts[prop] = info[key]
#                print "READ KEY", prop, opts[prop], type(info[key])
            if key in LIST_KEYS:
                prop = LIST_KEYS[key]
                if type(info[key]) == str:
                    opts[prop] = info[key].split(",")
                else:
                    opts[prop] = info[key]
#                print "READ KEY", prop, opts[prop], type(info[key])


def set(name, value):
    if not name in STRING_KEYS and not name in LIST_KEYS:
        print "NO SUCH CONFIG KEY: %s, IGNORING" % name
        return

    if name in STRING_KEYS:
        prop = STRING_KEYS[name]
        opts[prop] = value

    elif name in LIST_KEYS:
        prop = LIST_KEYS[name]

        if type(value) == str:
            opts[prop] = value.split(",")
        else:
            opts[prop] = value

#print "FILEKASTENDIR", FILEKASTEN_DIR
add_config_string("SECRET", default="changemeplease")
add_config_string("PORT", default=32333)
add_config_string("EXPORT_DIR", default=os.path.join(FILEKASTEN_DIR, "export"))
add_config_string("JOURNAL_DIR", default=os.path.join(FILEKASTEN_DIR, "journal"))
add_config_string("USE_NV_STYLE", default="")
add_config_string_list("DIRS", default={})
add_config_string_list("JOURNALS", [])
add_config_string_list("HIDDEN", default=[])
add_config_string_list("INCLUDE_RE", default="")
add_config_string_list("EXCLUDE_RE", default="")
add_config_string_list("HIDDEN_EXT", default="")

read_config()
