import flask
from . import config

from . import pudgy

class Crumb(dict):
    def __init__(self, name, url):
        self['name'] = name
        self['url'] = url

class Breadcrumbs(pudgy.JinjaComponent, pudgy.ServerBridge, pudgy.BackboneComponent):
    def __prepare__(self):
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
    b = Breadcrumbs(popup=True)
    self.html(b.render())

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
    crumbs = [w for w in crumbs if w.get("name") != name]
    flask.session["breadcrumbs"] = crumbs
