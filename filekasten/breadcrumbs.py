import flask
import config

import pydgeon

class Crumb(dict):
    def __init__(self, name, url):
        self['name'] = name
        self['url'] = url

class Breadcrumbs(pydgeon.JinjaComponent, pydgeon.ServerBridge):
    def __prep__(self):
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

        nv = config.opts.USE_NV_STYLE

        self.context.crumbs = ordered_crumbs
        self.context.nv = nv

        self.set_ref("breadcrumbs")

@Breadcrumbs.api
def refresh(self):
    b = Breadcrumbs()
    self.replace_html(b.render())

def add(name):
    crumbs = flask.session.get("breadcrumbs", [])
    # strip popup from breadcrumbs
    crumb = Crumb(name, flask.request.url.replace("&popup=1", ""))
    crumbs.append(crumb)
    if len(crumbs) > 50:
        crumbs = crumbs[-50:]

    flask.session["breadcrumbs"] = crumbs


def remove(name):
    crumbs = flask.session.get("breadcrumbs", [])
    crumbs = filter(lambda w: w.get("name") != name, crumbs)
    flask.session["breadcrumbs"] = crumbs
