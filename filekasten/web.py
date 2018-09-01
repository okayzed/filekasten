import re
import os
import datetime
import time

import markdown
from markdown.extensions.wikilinks import WikiLinkExtension

import yaml
import shlex
import flask
import frontmatter

import models
import breadcrumbs
import journal


import search
import config


CUR_DIR = os.path.dirname(os.path.realpath(__file__))
TEMPLATE_DIR=os.path.join(CUR_DIR, "templates")

NOTE_DIR = os.path.expanduser("~/Notes")

app = flask.Flask(__name__)

app.secret_key = config.SECRET
import datetime
def datetimeformat(value, format='%Y-%m-%d %H:%M'):
    if type(value) == int or type(value) == float:
        value = datetime.datetime.fromtimestamp(value)

    return value.strftime(format)

app.jinja_env.filters['format_datetime'] = datetimeformat
app.jinja_env.filters['format_dirname'] = lambda w: os.path.dirname(w or "???")
app.jinja_env.filters['format_filename'] = lambda w: os.path.basename(w or "???")

def yaml_dump(dict):
    s = yaml.dump(dict, default_flow_style=False)
    return s.strip("{}")

@app.before_request
def before_request():
    flask.g.request_start_time = time.time()
    flask.g.request_time = lambda: "%.5fs" % (time.time() - flask.g.request_start_time)
    flask.g.render_breadcrumbs = breadcrumbs.render_breadcrumbs


def readfile(fname):
    try:
        with open(fname) as f:
            rv = f.read()

        return rv
    except:
        return ""

def marshall_page(cur):
    text = ""
    if cur.filename:
        text = readfile(cur.filename)

    post = frontmatter.loads("")
    try:
        post = frontmatter.loads(text)
    except:
        post.content = text

    meta = post.metadata
    created = meta.get("created", cur.created)

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

    cur.content = post.content
    cur.metadata = meta
    cur.title = meta.get("title", "")
    cur.text = text

    return cur

from md_ext import XListExtension

def render_markdown(text):
    return markdown.markdown(text,
        tab_length=2,
        extensions=[
            WikiLinkExtension(base_url='/wiki/'),
	    XListExtension(),
            "markdown_checklist.extension",
            "markdown.extensions.footnotes",
            "markdown.extensions.codehilite",
            "markdown.extensions.fenced_code",
            "markdown.extensions.tables"]
    )

@app.route('/')
def index():
    return 'Off my lawn'

def get_pages():
    cur = models.Page.select(models.Page.name, models.Page.namespace,
        models.Page.journal, models.Page.hidden, models.Page.id)
    count = 0

    namespaces = {}
    for page in cur:
        if page.journal or page.hidden:
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

    return ns_keys, namespaces, count


@app.route('/wiki/')
def get_wiki_index(nv=False):
    breadcrumbs.add("index")
    k, n, count = get_pages()
    popup = flask.request.args.get("popup")
    return flask.render_template("index.html", namespaces=n, keys=k, total=count, filefinder=True, nv=nv, popup=popup)

@app.route('/nv/')
def get_nv_index():
    return get_wiki_index(nv=True)
    

@app.route('/wiki/<name>/')
def get_wiki_page(name):

    breadcrumbs.add(name)

    i = flask.request.args.get("i", -1)
    id = flask.request.args.get("id")

    try:
        if id:
            pages = list(models.Page.select().where(models.Page.id == id))
        else:
            pages = list(models.Page.select().where(models.Page.name == name))

        if not pages:
            raise models.Page.DoesNotExist('')

        if len(pages) > 1:
            if i == -1:
                return flask.render_template("wiki_select_page.html", pages=pages)

            cur = pages[i]
        else:
            cur = pages[0]

    except models.Page.DoesNotExist:
        cur = models.Page(name=name)

    page = marshall_page(cur)
    popup = flask.request.args.get("popup")

    text = render_markdown(page.content)

    k, n, count = get_pages()
    return flask.render_template("wiki_page.html", content=text, meta=page, page=cur,
        namespaces=n, keys=k, popup=popup)

@app.route("/wiki/<name>/terminal")
def get_terminal_page(name):
    print "TERMINAL", name
    id = flask.request.args.get('id')
    cur = models.Page.get(models.Page.id == id)
    page = marshall_page(cur)
    metadata = page.metadata
    namespace = page.namespace

    print "PAGE IS", cur


    import editor
    os.system("xfce4-terminal --working-directory='%s'" % (os.path.dirname(cur.filename)))

    return flask.redirect(flask.url_for("get_wiki_page", name=name, id=page.id))

@app.route("/wiki/<name>/edit")
def get_edit_page(name):
    print "GETTING PAGE", name
    cur = models.Page.get(models.Page.name == name)
    page = marshall_page(cur)
    metadata = page.metadata
    namespace = page.namespace

    print "PAGE IS", cur


    import editor
    status = editor.open(cur.filename)

    return flask.redirect(flask.url_for("get_wiki_page", name=name, id=cur.id))

@app.route("/append/")
def get_append_page():
    args = flask.request.args
    title = args.get('title', '')
    url = args.get('url', '')
    quote = args.get('quote', '')

    pages = list(models.Page.select(models.Page.name, models.Page.namespace,
        models.Page.journal, models.Page.hidden).execute());

    append_to = []
    for page in pages:
        if page.journal or page.hidden:
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
    quote = args.get('quote', '').strip()
    comments = args.get('comments')

    now = datetimeformat(datetime.datetime.fromtimestamp(time.time()))

    if quote:
        quote_str = "\n>%s" % quote.replace("\n", "\n>")
    else:
        quote_str = ""

    append_text = "\n-------\n**%s**\n[%s](%s) - %s%s\n\n%s" % (now, url, url, title, quote_str, comments)
    with open(cur.filename, "a") as f:
        f.write(append_text)

    search.index(cur)


    return flask.redirect(flask.url_for("get_wiki_page", name=name, id=cur.id, ts=time.time()))

@app.route("/journal/new/", methods=["POST"])
def post_new_journal():
    name = flask.request.form.get('name')
    split = shlex.split(name)

    page = journal.make_journal(split)
    if page:
        search.index(page)
        return flask.redirect(flask.url_for("get_wiki_page", name=page.name, id=page.id))



    return flask.redirect(flask.request.referrer or url_for('get_jrnl'))

@app.route("/new/", methods=["POST"])
def post_new_page():
    args = flask.request.form
    name = args.get('name')

    page = models.Page.select().where(models.Page.name == name)
    if len(page) == 0:
        name = os.path.normpath(name)
        if name.find("..") != -1 or name[0] == '/':
            print "INVALID PATH", name
            return "INVALID PAGE NAME: %s, PLEASE REMOVE THE '..' and leading '/'" % (name)

        namespace, pagename = os.path.split(name)
        path = os.path.join(NOTE_DIR, namespace)
        if not os.path.exists(path):
            os.makedirs(path)

        page_path = os.path.join(path, pagename)

        aname = os.path.abspath(page_path)
        with open(page_path, "a") as f:
            f.write("")

        created = time.time()
        page = models.Page(
          name=pagename,
          title='',
          created=created,
          filename=aname,
          namespace=namespace,
          journal=False,
          hidden=False,
          type="markdown",
          updated=created
          )
        search.index(page)

        page.save()
    else:
        print "PAGE ALREADY EXISTS", name
        pagename = name

    return flask.redirect(flask.url_for("get_wiki_page", name=pagename, id=page.id, ts=time.time()))



@app.route('/breadcrumbs/remove', methods=["POST"])
def delete_breadcrumb():
    name = flask.request.form.get('name')
    if name:
        breadcrumbs.remove(name)
    return flask.redirect(flask.url_for("get_wiki_index"))


@app.route('/jrnl/')
def get_jrnl():
    n = flask.request.args.get('n', 30)

    jrnl = (models.Page
        .select()
        .where(models.Page.journal == True)
        .order_by(models.Page.created.desc())
        .limit(n)
        .execute())


    entries = map(marshall_page, jrnl)
    entries.sort(key=lambda w: w.created, reverse=True)

    k, n, count = get_pages()
    return flask.render_template("jrnl_page.html", entries=entries, render=render_markdown, namespaces=n, keys=k)

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
    breadcrumbs.add("search: " + query)

    results = (models.Page.select()
        .join(
            models.PageIndex,
            on=(models.Page.id == models.PageIndex.rowid))
        .where(models.PageIndex.match(query))

        )


    query_re = re.compile(query, re.IGNORECASE)
    def highlight_search(line, query):
        return query_re.sub("<b class='match'>%s</b>" % (query), line)

    for r in results:
        page = marshall_page(r)
        r.snippets = make_snippets(page, query, highlight_search)



    k, n, count = get_pages()
    return flask.render_template("search_results.html",
        results=results,
        search=query,
        namespaces=n,
        keys=k,
        highlight_search=highlight_search,
        query=query)

if __name__ == "__main__":
    import maintenance

    def sleep_idle():
        import time
        while True:
            time.sleep(1)
    maintenance.start_threads(sleep_idle)
