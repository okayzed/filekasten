import os
import datetime
import time
import html2text

import markdown
from markdown.extensions.wikilinks import WikiLinkExtension

import babel.dates
import flask
import jinja2
import frontmatter

import models

import yaml
import search


CUR_DIR = os.path.dirname(os.path.realpath(__file__))
TEMPLATE_DIR=os.path.join(CUR_DIR, "templates")

app = flask.Flask(__name__)
import datetime
def datetimeformat(value, format='%Y-%m-%d %H:%M'):
    if type(value) == int or type(value) == float:
        value = datetime.datetime.fromtimestamp(value)

    return value.strftime(format)

app.jinja_env.filters['format_datetime'] = datetimeformat

def yaml_dump(dict):
    s = yaml.dump(dict, default_flow_style=False)
    return s.strip("{}")

@app.before_request
def before_request():
    flask.g.request_start_time = time.time()
    flask.g.request_time = lambda: "%.5fs" % (time.time() - flask.g.request_start_time)


def marshall_page(cur):
    text = cur.text
    post = frontmatter.loads(text)

    meta = post.metadata
    created = meta.get("created", cur.created)
    title = meta.get("title", cur.title)

    ts = None
    if created:
        if type(created) == str:
            if created.find("-") != -1:
                ts = datetime.datetime.strptime(created, '%Y-%m-%d %H:%M:%p')
            else:
                ts = datetime.datetime.fromtimestamp(created)
        else:
            ts = created

    cur.created = meta.get("created", ts)
    cur.title = meta.get("title", title)

    cur.content = post.content
    cur.metadata = meta

    return cur

def render_markdown(text):
    return markdown.markdown(text,
        extensions=[
            WikiLinkExtension(base_url='/wiki/'),
            "markdown_checklist.extension",
            "markdown.extensions.footnotes",
            "markdown.extensions.sane_lists",
            "markdown.extensions.tables"]
    )

@app.route('/')
def index():
    return 'Off my lawn'

@app.route('/wiki/')
def get_wiki_index():
    cur = models.Page.select()
    count = 0

    namespaces = {}
    for page in cur:
        if page.namespace.find("jrnl") != -1 or page.namespace.find("sjrn") != -1:
            continue

        if not page.namespace in namespaces:
            ns = []
            namespaces[page.namespace] = ns
        else:
            ns = namespaces[page.namespace]

        ns.append(page)
        count += 1

    for ns in namespaces:
        namespaces[ns].sort(key=lambda w: w.name.lower())

    ns_keys = namespaces.keys()
    ns_keys.sort()

    return flask.render_template("index.html", namespaces=namespaces, keys=ns_keys, total=count)

@app.route('/wiki/<name>/')
def get_wiki_page(name):
    cur = models.Page.get(models.Page.name == name)

    page = marshall_page(cur)

    if cur.type == "markdown":
        text = render_markdown(page.content)

    return flask.render_template("wiki_page.html", content=text, meta=page, page=cur)

@app.route("/wiki/<name>/edit")
def get_edit_page(name):
    try:
        cur = models.Page.get(models.Page.name == name)
        page = marshall_page(cur)
        metadata = page.metadata
        text = page.content
        namespace = page.namespace
    except:
        cur = None
        page = {}
        metadata = {}
        text = ""
        namespace = ""


    if cur and cur.type == "markdown":
        text = render_markdown(page.content)

    return flask.render_template("wiki_edit.html",
        content=text, metadata=metadata, yaml_dump=yaml_dump, name=name,
        namespace=namespace)

@app.route("/wiki/<name>/edit", methods=["POST"])
def post_edit_page(name):
    print "POST EDIT PAGE", name
    args = flask.request.form
    namespace = args.get('namespace')

    try:
        cur = models.Page.get(models.Page.name == name)
    except:
        cur = models.Page(
            name=name,
            type="markdown",
            title=name,
            filename="%s/%s" % (namespace, name),
            edit_count=0)

    cur.text = args.get('text', "")
    cur.namespace = namespace
    cur.edit_count = cur.edit_count+1
    cur.text = "---\n%s\n\n---\n\n%s" % (args.get("metadata"), cur.text.encode("utf-8"))
    cur.save()

    print type(cur.text)

    search.index(cur)

    return flask.redirect(flask.url_for("get_wiki_page", name=name))

@app.route("/append/")
def get_append_page():
    args = flask.request.args
    title = args.get('title', '')
    url = args.get('url', '')
    quote = args.get('quote', '')

    pages = list(models.Page.select(models.Page.name, models.Page.namespace).execute());
    append_to = []
    hidden = ["jrnl", "sjrn", "rambles"]
    for page in pages:
        hide = False
        for h in hidden:
            if page.namespace.find(h) != -1:
                hide = True
                continue
        if hide:
            continue

        append_to.append(page)

    append_to.sort(key=lambda w: w.created, reverse=True)


    return flask.render_template("wiki_append.html", url=url, title=title, quote=quote, pages=append_to)

@app.route("/append/", methods=["POST"])
def post_append_page():
    args = flask.request.form
    name = args.get('name')
    cur = models.Page.get(models.Page.name == name)

    title = args.get('title')
    url = args.get('url')
    quote = args.get('quote')
    comments = args.get('comments')


    return flask.redirect(flask.url_for("get_wiki_page", name=name))

@app.route('/jrnl/')
def get_jrnl():
    sjrn = models.Page.select().where(models.Page.namespace == "sjrn").execute()
    jrnl = models.Page.select().where(models.Page.namespace == "jrnl").execute()

    entries  = map(marshall_page, sjrn)
    entries.extend(map(marshall_page, jrnl))
    entries.sort(key=lambda w: w.created, reverse=True)

    return flask.render_template("jrnl_page.html", entries=entries, render=render_markdown)

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

@app.route('/search/')
def get_search():
    args = flask.request.args
    query = args.get('q')

    results = (models.Page.select()
        .join(
            models.PageIndex,
            on=(models.Page.id == models.PageIndex.rowid))
        .where(models.PageIndex.match(query))

        )

    import re

    query_re = re.compile(query, re.IGNORECASE)
    def highlight_search(line, query):
        return query_re.sub("<s>%s</s>" % (query), line)

    for r in results:
        page = marshall_page(r)
        r.snippets = make_snippets(page, query, highlight_search)



    return flask.render_template("search_results.html",
        results=results,
        highlight_search=highlight_search,
        query=query)

if __name__ == "__main__":
    app.run(use_debugger=True)

