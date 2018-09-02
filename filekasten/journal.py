import config
import os
import tempfile
import time
import frontmatter
import subprocess

import models

JOURNAL_DIR = config.opts.JOURNAL_DIR
if not os.path.exists(JOURNAL_DIR):
    os.makedirs(JOURNAL_DIR)

EDITOR = os.environ.get("EDITOR", "vim")
# @journal
# :group1 :group2
def make_journal(args):
    groups = []
    tags = []
    journal = None

    for arg in args:
        # @ symbol is always tags
        if arg[0] == "@":
            tags.append(arg[1:])
        elif arg[0] == ".":
            journal = arg[1:]
        elif arg[0] == ":":
            groups.append(arg[1:])


    fd, fname = tempfile.mkstemp()
    f = os.fdopen(fd, "w")

    meta = {
        "created" : time.time(),
        "journal" : journal,
        "groups" : groups,
        "tags" : tags
    }


    post = frontmatter.loads("")
    post.metadata = meta

    frontmatter.dump(post, f)
    f.close()

    terminal = "xfce4-terminal -x"
    editor = os.environ.get("EDITOR", "vim")

    command = terminal + " " + editor + " " + fname
    ret = subprocess.call(command, shell=True)
    newpost = frontmatter.load(open(fname, "r"))
    os.remove(fname)

    if newpost.content and newpost.content.strip() != "":

        fd, fname = tempfile.mkstemp(dir=JOURNAL_DIR, prefix='post', suffix='cli')
        f = os.fdopen(fd, "w")

        frontmatter.dump(newpost, f)
        f.close()

        aname = os.path.abspath(fname)
        basedir,filename = os.path.split(fname)
        page = models.Page(filename=aname, name=filename, namespace='journal', journal=True, hidden=True)
        page.save()
        print "SAVED JOURNAL ENTRY TO", fname
        return page

