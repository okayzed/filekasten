import argparse
import os
import time

import frontmatter
import datetime
import yaml
import re

import models
import search
import config

from web import marshall_page

parser = argparse.ArgumentParser(description='Import flatfiles into the sqlite DB')
parser.add_argument('-d', '--dir', help='import files from dir')
parser.add_argument('-n', '--namespace', help='namespace to import into', default="")
parser.add_argument('-y', '--yaml', help='yaml config file for importing', default="")


def main():
  pass

textchars = bytearray({7,8,9,10,12,13,27} | set(range(0x20, 0x100)) - {0x7f})
def is_binary(filename):
    is_binary_string = lambda bytes: bool(bytes.translate(None, textchars))
    return is_binary_string(open(filename, 'rb').read(1024))


def path_walker(dir, visited=None, namespace=None, journals=None, hidden=None):
  if not visited:
    visited = {}

  now = time.time()
  try:
      files = os.listdir(dir)
  except:
    return

  for file in files:
    fname = os.path.join(dir, file)
    aname = os.path.abspath(fname)

    wikiname = file
    if namespace:
      wikiname = "%s/%s" % (namespace, file)

    stats = os.stat(fname)

    if file[0] == ".":
      continue

    basename, ext = os.path.splitext(file)
    # TODO: check the config for regexes, i guess
    include = False
    exclude = False
    for r in config.opts.INCLUDE_RE:
        if not r:
            continue

        if re.match(r, file):
            include = True
            break

    if not include:
        for r in config.opts.EXCLUDE_RE:
            if not r:
                continue

            if re.search(r, file):
                exclude = True
                break

    if exclude:
        print "EXCLUDING", file
        continue

    if ext in [".html", ".css", ".json"] or file.find(".input") != -1 or file.find(".output") != -1:
        print "SKIPPING KNOWN EXTENSIONS", file
        continue

    if file.find("icfpc") != -1:
        continue

    if stats.st_size > 1024 * 1024:
        print "SKIPPING", aname, "ITS TOO BIG"
        continue


    if os.path.isdir(fname) and not fname in visited:
      visited[fname] = True
      path_walker(fname, visited, namespace=os.path.join(namespace, file),journals=journals, hidden=hidden)
      continue

    visited[fname] = True


    if is_binary(aname):
        continue

    with open(fname, "r") as f:
      content = f.read()

    try:
      oldpage = models.Page.get(models.Page.filename == aname)
    except models.Page.DoesNotExist:
      oldpage = None

    if oldpage:
      mt = datetime.datetime.fromtimestamp(stats.st_mtime)

      # chop off microseconds
      mt = mt - datetime.timedelta(microseconds=mt.microsecond)

      if oldpage.updated < mt:
        (oldpage
          .update(updated=mt)
          .where(models.Page.filename == aname)
          .execute())

        search.index(oldpage)
    else:
      print "INGESTING", fname, "INTO", namespace
      try:
          mp = frontmatter.loads(content)
      except:
          mp = frontmatter.loads('')
          mp.content = content

      created = mp.metadata.get('created')

      if created:
        try:
          created = float(created)
        except:
          created = created.toordinal()
      else:
        created = stats.st_mtime


      page = models.Page(
        name=file,
        title=mp.metadata.get('title', ''),
        created=created,
        filename=aname,
        namespace=namespace,
        type="markdown",
        updated=stats.st_mtime,
        journal=namespace in journals,
        hidden=namespace in hidden,
        )

      try:
          search.index(page)
          page.save()
      except:
          print "COULDNT INDEX PAGE", page.name

def ingest_files(dirs, journals, hidden):
    print "INGESTING FILES"
    dirs[config.opts.JOURNAL_DIR] = 'journal'

    for k in dirs:
      v = dirs[k]
      print "READING DIR", k, "INTO", v
      path = os.path.expanduser(k)
      path_walker(path,namespace=v,journals=journals,hidden=hidden)

if __name__ == "__main__":
  args = parser.parse_args()
  if args.yaml:
    with open(args.yaml) as f:
      d = yaml.load(f.read())

      journals = set(d.get('journal', []))
      hidden = set(d.get('hidden', []))
      dirs = d.get('dirs', {})

      ingest_files(dirs, journals, hidden)


  if args.dir:
    path_walker(args.dir,namespace=args.namespace)
