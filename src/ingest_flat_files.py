import argparse
import os
import time

import frontmatter
import datetime
import yaml

import models
import search
from web import marshall_page

parser = argparse.ArgumentParser(description='Import flatfiles into the sqlite DB')
parser.add_argument('-d', '--dir', help='import files from dir')
parser.add_argument('-n', '--namespace', help='namespace to import into', default="")
parser.add_argument('-y', '--yaml', help='yaml config file for importing', default="")


def main():
  pass


def path_walker(dir, visited=None, namespace=None):
  if not visited:
    visited = {}

  now = time.time()
  files = os.listdir(dir)
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
    if ext == ".html" or ext == ".css":
      continue


    if os.path.isdir(fname) and not fname in visited:
      visited[fname] = True
      path_walker(fname, visited, namespace=os.path.join(namespace, file))
      continue

    visited[fname] = True


    with open(fname, "r") as f:
      content = f.read()

    try:
      oldpage = models.Page.get(models.Page.name == file)
    except models.Page.DoesNotExist:
      oldpage = None

    if oldpage:
      mt = datetime.datetime.fromtimestamp(stats.st_mtime)

      if oldpage.updated < mt:
        (oldpage
          .update(updated=now)
          .where(models.Page.name==file)
          .execute())

        search.index(oldpage)
    else:
      print "INGESTING", fname, "INTO", namespace
      mp = frontmatter.loads(content)
      created = mp.metadata.get('created')

      if created:
        try:
          created = float(created)
        except:
          created = created.toordinal()
      else:
        created = stats.st_ctime


      page = models.Page(
        name=file,
        title=mp.metadata.get('title', ''),
        created=created,
        filename=aname,
        namespace=namespace,
        type="markdown",
        updated=stats.st_mtime,
        )

      page.save()
      search.index(page)

if __name__ == "__main__":
  args = parser.parse_args()
  if args.yaml:
    with open(args.yaml) as f:
      d = yaml.load(f.read())

      dirs = d.get('dirs')
      for k in dirs:
        v = dirs[k]
        print "READING DIR", k, "INTO", v
        path = os.path.expanduser(k)
        path_walker(path,namespace=v)


  if args.dir:
    path_walker(args.dir,namespace=args.namespace)
