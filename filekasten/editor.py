import os, tempfile

def edit(content=''):
    editor = os.environ["EDITOR"]
    f = tempfile.NamedTemporaryFile(mode='w+')
    if content:
        f.write(content)
        f.flush()

    terminal = "xfce4-terminal -x"
    command = terminal + " " + editor + " " + f.name
    status = os.system(command)
    f.seek(0, 0)
    text = f.read()
    f.close()
    assert not os.path.exists(f.name)
    return (status, text)

def open(fname):
    basedir = os.path.dirname(fname)
    terminal = "xfce4-terminal --working-directory='%s' -x" % basedir

    if not os.path.exists(fname):
        raise Exception("Path does not exist")

    editor = os.environ["EDITOR"]
    command = terminal + " " + editor + " " + fname
    status = os.system(command)
    return status
