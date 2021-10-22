from . import models
import sys
import os

from importlib import reload
reload(sys)


def index(page):
    with open(page.filename) as f:
        content = f.read()

    try:
        et = models.PageIndex.get(models.PageIndex.rowid == page.id)
    except models.PageIndex.DoesNotExist:
        et = None

    if type(content) != str:
        content = str(content, "utf-8")

    if not et:
        print("INDEXING", page.name)
        sql = models.PageIndex.insert(
            name=page.name, 
            content=content,
            rowid=page.id)

        sql.execute()

    else:
        print("UPD INDEXING", page.name)
        et.update(
            name=page.name,
            content=content,
        ).where(models.PageIndex.rowid == page.id).execute()

def make_snippets(page, query, highlight_search):
    text = page.content
    lines = text.split("\n")

    snippets = []
    prev = None
    snippet = []
    index = 0
    for line in lines:

        line = "%s:%s" % (index, highlight_search(line, query))
        index += 1
        if line.find(query) != -1:
            if prev and not snippet:
                snippet.append(prev)
            snippet.append(line)
        elif snippet:
            snippet.append(line)
            snippets.append("\n".join(snippet))
            snippet = []

        prev = line

    if snippet:
        snippets.append("\n".join(snippet))

    return snippets

