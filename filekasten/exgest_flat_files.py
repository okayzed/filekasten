import argparse
import os
import time
import frontmatter

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

if __name__ == "__main__":
  args = parser.parse_args()
  if args.dir:
    export_files_to_dir(args.dir)
