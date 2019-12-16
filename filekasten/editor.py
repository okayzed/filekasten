import os, tempfile
import subprocess

import terminal

def call(cmd):
    subprocess.call(cmd, shell=True)

def edit(content=''):
    editor = os.environ.get("EDITOR", "vim")
    f = tempfile.NamedTemporaryFile(mode='w+')
    if content:
        f.write(content)
        f.flush()

    cmd = "%s -x" % (terminal.CMD)
    command = cmd + " " + editor + " " + f.name
    status = call(command)
    f.seek(0, 0)
    text = f.read()
    f.close()
    assert not os.path.exists(f.name)
    return (status, text)

def open(fname):
    basedir = os.path.dirname(fname)
    cmd = "%s --working-directory='%s' -x" % (terminal.CMD, basedir)

    if not os.path.exists(fname):
        raise Exception("Path does not exist")

    editor = os.environ.get("EDITOR", "vim")
    command = "%s %s '%s'" % (cmd, editor, fname)
    status = call(command)
    return status
