import argparse
import os
import time
import frontmatter
import subprocess

import models
from flask_peewee.utils import get_dictionary_from_model

from web import marshall_page

# this will export a directory full of files and a script to copy them into their original
# directories
parser = argparse.ArgumentParser(description='Exgest flatfiles from the sqlite DB')
parser.add_argument('-d', '--dir', help='exgest files into dir')

def marshall_post(cur):
    # turns a Page into a frontmatter Post
    post = frontmatter.loads("")
    page = marshall_page(cur)
    post.content = page.text.encode('ascii', 'ignore')
    post.metadata.update(get_dictionary_from_model(cur))
    if "text" in post.metadata:
        del post.metadata["text"]

    return post

def export_files_to_dir(outdir):
    results = (models.Page.select())
    base_dir = os.path.normpath(outdir)
    count = 0
    for r in results:
        # export each and every page
        dest = os.path.join(base_dir, r.namespace, r.name)
        basename = os.path.dirname(dest)
        try:
            os.makedirs(basename)
        except:
            pass

        with open(os.path.join(basename, "diff.sh"), "a") as f:
            f.write("diff -y '%s' '%s'\n" % (dest, r.filename))
#        with open(os.path.join(basename, "restore.sh"), "a") as f:
#            f.write("cp '%s' '%s'\n" % (dest, r.filename))

#        print "EXPORTING", r.filename, "TO", dest
        with open(dest, "w") as f:
            page = marshall_post(r)
            f.write(frontmatter.dumps(page))

        count += 1

    print "EXPORTED", count, "FILES TO", outdir

    make_git_commit(outdir)

def make_git_commit(outdir):
    outdir = os.path.abspath(outdir)
    print "OUTDIR", outdir
    import shlex
    def run_command(cmd):
        cmd_args = shlex.split(cmd)
        print list(cmd_args)
        output = subprocess.check_output(cmd_args, cwd=outdir)

    try:
        run_command("/usr/bin/git status")
    except subprocess.CalledProcessError:
        run_command("/usr/bin/git init .")

    run_command("/usr/bin/git add .")
    from web import datetimeformat
    date_str = datetimeformat(time.time())
    try:
        run_command("/usr/bin/git commit -a -v -m '[autocommit] %s'" % date_str)
    except Exception, e:
        # likely there is nothing to commit
        print e


    # we assume the outdir is the git dir for us
    pass

if __name__ == "__main__":
  args = parser.parse_args()
  if args.dir:
    export_files_to_dir(args.dir)
