import pudgy
import os

from pudgy import FlaskPage

import markdown

import pygments
import pygments.lexers
import pygments.formatters

from pudgy.util import memoize

from md_ext import XListExtension, WikiLinkExtension

@memoize
def render_markdown(text):
    return markdown.markdown(text,
        tab_length=2,
        extensions=[
            WikiLinkExtension(base_url='/wiki/'),
            XListExtension(),
            "markdown.extensions.footnotes",
            "markdown.extensions.codehilite",
            "markdown.extensions.fenced_code",
            "markdown.extensions.tables"]
    )

class WikiIndex(pudgy.FlaskPage):
    pass

class JournalPage(pudgy.FlaskPage):
    pass

class JournalEntry(pudgy.JinjaComponent):
    def __prepare__(self):
        self.context.title = render_markdown(self.context.entry.title)
        self.context.content = render_markdown(self.context.entry.content)

class WikiPage(pudgy.FlaskPage, pudgy.BackboneComponent):
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

class SettingsPage(pudgy.FlaskPage, pudgy.BackboneComponent):
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
    pudgy.Component.set_base_dir(os.path.join(app.root_path, "components"))
    pudgy.register_blueprint(app)
    app.after_request(pudgy.compress_request)
