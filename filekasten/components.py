import pudgy
import os

from pudgy import FlaskPage

import markdown

import pygments
import pygments.lexers
import pygments.formatters

from pudgy.util import memoize

from md_ext import XListExtension, WikiLinkExtension
import datetime

import config

@memoize
def render_markdown(text):
    return markdown.markdown(text,
        tab_length=2,
        extensions=[
            WikiLinkExtension(base_url='/wiki/', end_url=".md"),
            XListExtension(),
            "markdown.extensions.footnotes",
            "markdown.extensions.codehilite",
            "markdown.extensions.fenced_code",
            "markdown.extensions.tables"]
    )

class BasePage(pudgy.FlaskPage):
    def __init__(self, *args, **kwargs):
        super(BasePage, self).__init__(*args, **kwargs)
        self.context.config = config

class WikiIndex(BasePage):
    pass

class JournalPage(BasePage):
    pass

class TodoPage(BasePage):
    pass

class EntryListing(pudgy.JinjaComponent, pudgy.NoJSPagelet):
    def __init__(self, *args, **kwargs):
        self.delay = 0
        super(EntryListing, self).__init__(*kwargs, **kwargs)

    def set_delay(self, d):
        self.delay = d

    def __prepare__(self):
        es = []
        for e in self.context.entries:
            if type(e.created) == int or type(e.created) == float:
                e.created = datetime.datetime.fromtimestamp(e.created)
    
            es.append(JournalEntry(entry=e))

        self.context.entries = es


class JournalEntry(pudgy.MustacheComponent):
    def __prepare__(self):
        from web import datetimeformat
        import flask
        self.context.title = render_markdown(self.context.entry.title)
        self.context.content = render_markdown(self.context.entry.content)
        self.context.entry.format_created = datetimeformat(self.context.entry.created)
        self.context.entry.url = flask.url_for("get_wiki_page", name=self.context.entry.name)
        self.context.namespace = self.context.entry.namespace;

class WikiPage(BasePage, pudgy.BackboneComponent):
    def __prepare__(self):
        page = self.context.page
        root,ext = os.path.splitext(page.filename)

        try:
            lexer = pygments.lexers.get_lexer_for_filename(page.filename)
        except pygments.lexers.ClassNotFound:
            lexer = None

        formatter = pygments.formatters.HtmlFormatter(linenos='table')

        css_defs = ""
        singlecol = False
        if not lexer or type(lexer) in [pygments.lexers.MarkdownLexer, pygments.lexers.TextLexer]:
            text = render_markdown(page.content)
        else:
            text = pygments.highlight(page.content, lexer, formatter)
            css_defs = formatter.get_style_defs()
            singlecol = True

        # attach our prepared data to our context
        self.context.content = text
        self.context.css_defs = css_defs
        self.context.singlecol = singlecol

class SettingsPage(BasePage, pudgy.BackboneComponent):
    pass

class SearchBar(pudgy.BackboneComponent, pudgy.MustacheComponent):
    pass

class PageListing(pudgy.JinjaComponent):
    pass

class PageFinder(pudgy.BackboneComponent, pudgy.JinjaComponent):
    pass

class NVViewer(pudgy.JinjaComponent):
    pass

class Typeahead(pudgy.BackboneComponent, pudgy.JinjaComponent):
    pass

def install(app):
    pudgy.add_to_prelude("jquery", os.path.join(app.static_folder, "jquery-3.3.1.min.js"))
    pudgy.add_prelude_line("window.jQuery = window.$ = require('jquery')")

    pudgy.register_blueprint(app)
    app.after_request(pudgy.compress_request)
