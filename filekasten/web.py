import re
import os
import datetime
import time
import urllib

import markdown
import jinja2

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
app.secret_key = config.opts.SECRET

app.config["SESSION_COOKIE_NAME"] = "filekasten"



# install pudgy component library
from components import *
import components
components.install(app)

import pudgy
pudgy.use_jquery()

import datetime
def datetimeformat(value, format='%Y-%m-%d %H:%M'):
    if type(value) == int or type(value) == float:
        value = datetime.datetime.fromtimestamp(value)

    return value.strftime(format)

app.jinja_env.filters['format_datetime'] = datetimeformat
app.jinja_env.filters['format_dirname'] = lambda w: os.path.dirname(w or "???")
app.jinja_env.filters['format_filename'] = lambda w: os.path.basename(w or "???")

@app.before_request
def before_request():
    flask.g.request_start_time = time.time()
    flask.g.request_time = lambda: "%.5fs" % (time.time() - flask.g.request_start_time)
    flask.g.render_breadcrumbs = lambda: breadcrumbs.Breadcrumbs().set_ref("breadcrumbs")


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

def get_entry_listing(entries):
    entrylisting = EntryListing()
    entrylisting.async()
    entrylisting.context.update(entries=entries)
    return entrylisting

def get_page_listing(filefinder=False, nv=False):
    k, n, count = get_pages()
    popup = flask.request.args.get("popup")
    return PageListing(
        namespaces=n,
        total=count,
        popup=popup,
        filefinder=filefinder,
        keys=k,
        nv=nv
    )


def get_pages():
    cur = models.Page.select(models.Page.name, models.Page.namespace,
        models.Page.journal, models.Page.hidden, models.Page.id)
    count = 0

    namespaces = {}
    for page in cur:
        if page.journal or page.hidden or page.namespace in config.opts.JOURNALS:
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


@app.route('/')
def index():
    return 'Off my lawn'

@app.route('/wiki/')
def get_wiki_index(nv=False):
    nv = config.opts.USE_NV_STYLE
    if not nv:
        breadcrumbs.add("index")

    popup = flask.request.args.get("popup")
    pagelisting = get_page_listing(filefinder=True, nv=nv)
    pf = False
    if nv and not popup:
        pf = True
        component = NVViewer(pagelisting=pagelisting)
    else:
        component = pagelisting

    pagefinder = PageFinder(component=component).marshal(page_finder=pf)

    return WikiIndex(template="index.html", pagefinder=pagefinder, popup=popup).render()

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
    nv = config.opts.USE_NV_STYLE

    if not popup and nv:
        return flask.redirect(flask.url_for("get_wiki_index") + "#" +
            flask.url_for("get_wiki_page", name=page.name, id=page.id))



    pagelisting = get_page_listing(nv=False)

    return WikiPage(template="wiki_page.html",
            page=page,
            pagelisting=pagelisting,
            popup=popup,
        ).marshal(
            page=cur.name, pageid=page.id
        ).render()

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
    id = flask.request.args.get('id')
    cur = models.Page.get(models.Page.name == name, models.Page.id == id)
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
    search = args.get('search', '')

    pages = list(models.Page.select(models.Page.name, models.Page.namespace,
        models.Page.journal, models.Page.hidden).execute());

    append_to = []
    for page in pages:
        if page.journal or page.hidden or page.namespace in config.opts.JOURNALS:
            continue

        append_to.append(page)

    append_to.sort(key=lambda w: w.created, reverse=True)


    typeahead = Typeahead().marshal(options=[p.name for p in append_to])

    return FlaskPage(template="wiki_append.html", url=url, title=title, quote=quote,
        pages=append_to, typeahead=typeahead, search=search).render()

@app.route("/append/", methods=["POST"])
def post_append_page():
    args = flask.request.form
    name = args.get('name')

    # TODO: get or create needs to create this file if it doesn't exist
    cur = models.Page.select().where(models.Page.name == name)
    if len(cur) == 0:
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
        cur = models.Page(
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
        search.index(cur)

        cur.save()
    else:
        cur = cur[0]

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

    print flask.request.form

    next = flask.request.form.get('next', flask.url_for("get_wiki_index"))
    next = urllib.unquote(next)
    print "NEXT IS", next
    return flask.redirect(next)


@app.route('/breadcrumbs/')
def get_breadcrumbs():
    return breadcrumbs.render_breadcrumbs()

def get_journal_entries(page, per_page):
    jrnl = (models.Page
        .select()
        .where(models.Page.namespace << config.opts.JOURNALS)
        .order_by(models.Page.created.desc())
        .paginate(page, per_page))

    jrnl.execute()


    return map(marshall_page, jrnl)

def get_todo_entries(page, per_page):
    todo = (models.Page.select()
        .join(
            models.PageIndex,
            on=(models.Page.id == models.PageIndex.rowid))
        .where(models.PageIndex.match("todo"))
        .order_by(models.Page.updated.desc())

        )
    todo.execute()


    return map(marshall_page, todo)

@app.route('/jrnl/')
def get_jrnl():
    n = flask.request.args.get('n', 50)

    es = []
    for i in xrange(1, 3):
        entries = get_journal_entries(i, n)
        entrylisting = get_entry_listing(entries)
#        entrylisting.set_delay(i-1)
        es.append(entrylisting)


    nv = config.opts.USE_NV_STYLE
    pagelisting = get_page_listing(filefinder=True, nv=nv)
    pf = False
    if nv:
        component = NVViewer(pagelisting=pagelisting)
    else:
        component = pagelisting

    ret= JournalPage(
            template="jrnl_page.html",
            entries=es,
            pagelisting=pagelisting,
        ).pipeline()
    return ret

@app.route('/todo')
def get_todo():
    n = flask.request.args.get('n', 50)

    es = []
    for i in xrange(1, 3):
        entries = get_todo_entries(i, n)
        entrylisting = get_entry_listing(entries)
    #        entrylisting.set_delay(i-1)
        es.append(entrylisting)


    nv = config.opts.USE_NV_STYLE
    pagelisting = get_page_listing(filefinder=True, nv=nv)
    pf = False
    if nv:
        component = NVViewer(pagelisting=pagelisting)
    else:
        component = pagelisting

    ret= TodoPage(
            template="todo_page.html",
            entries=es,
            pagelisting=pagelisting,
        ).pipeline()
    return ret

@app.route('/search/')
def get_search():
    args = flask.request.args
    query = args.get('q')
    breadcrumbs.add("search: " + query)
    popup = flask.request.args.get("popup")

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
        r.snippets = search.make_snippets(page, query, highlight_search)


    pagelisting = get_page_listing()
    return FlaskPage(template="search_results.html",
        results=results,
        search=query,
        popup=popup,
        pagelisting=pagelisting,
        highlight_search=highlight_search,
        query=query).render()

@app.route('/settings/')
def get_settings():

    sp = SettingsPage(template="settings.html")
    sp.context.update(config=config)

    return sp.render()

@app.route('/settings/', methods=["POST"])
def post_settings():
    args = flask.request.form
    print "POSTED SETTINGS", args
    dirs = args.getlist('dir[]')
    namespace = args.getlist('namespace[]')
    type = args.getlist('type[]')

    objects = {}
    journals = []
    hidden = []
    for i in xrange(len(dirs)):
        o = {}
        objects[dirs[i]] = namespace[i]


    config.set("DIRS", objects)
    config.set("USE_NV_STYLE", args.get("USE_NV_STYLE", ""))
    config.update(args)
    config.save_config()

    return flask.render_template("settings.html", config=config)


if __name__ == "__main__":
    import maintenance

    def sleep_idle():
        import time
        while True:
            time.sleep(1)
    maintenance.start_threads(sleep_idle)
