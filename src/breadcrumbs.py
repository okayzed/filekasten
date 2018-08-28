import flask

class Crumb(dict):
    def __init__(self, name, url):
        self['name'] = name
        self['url'] = url



def render_breadcrumbs(*args):
    crumbs = flask.session.get("breadcrumbs", [])
    seen = {}
    ordered_crumbs = []
    for crumb in reversed(crumbs):
        if crumb.get("name") in seen:
            continue

        seen[crumb.get("name")] = True

        ordered_crumbs.append(crumb)

        if len(ordered_crumbs) > 7:
            break

    return flask.render_template("breadcrumbs.html", crumbs=ordered_crumbs)

def add(name):
    crumbs = flask.session.get("breadcrumbs", [])
    crumb = Crumb(name, flask.request.url)
    crumbs.append(crumb)
    if len(crumbs) > 50:
        crumbs = crumbs[-50:]

    flask.session["breadcrumbs"] = crumbs


def remove(name):
    crumbs = flask.session.get("breadcrumbs", [])
    crumbs = filter(lambda w: w.get("name") != name, crumbs)
    flask.session["breadcrumbs"] = crumbs
