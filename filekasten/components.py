import pydgeon
import os


class WikiIndex(pydgeon.FlaskPage):
    pass

class WikiPage(pydgeon.FlaskPage):
    pass

class SearchBar(pydgeon.BackboneComponent, pydgeon.MustacheComponent):
    pass

class PageListing(pydgeon.BackboneComponent):
    pass

class PageFinder(pydgeon.BackboneComponent):
    pass

class Typeahead(pydgeon.BackboneComponent):
    pass

def install(app):
    pydgeon.Component.set_base_dir(os.path.join(app.root_path, "components"))
    pydgeon.install(app)
