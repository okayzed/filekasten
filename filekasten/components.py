import pydgeon
import os

from pydgeon import FlaskPage

import markdown

import pygments
import pygments.lexers
import pygments.formatters

from pydgeon.util import memoize

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

class WikiIndex(pydgeon.FlaskPage):
    pass

class JournalPage(pydgeon.FlaskPage):
    pass

class JournalEntry(pydgeon.JinjaComponent):
    def __prepare__(self):
        self.context.title = render_markdown(self.context.entry.title)
        self.context.content = render_markdown(self.context.entry.content)

class WikiPage(pydgeon.FlaskPage, pydgeon.BackboneComponent):
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

class SettingsPage(pydgeon.FlaskPage, pydgeon.BackboneComponent):
    pass

class SearchBar(pydgeon.BackboneComponent, pydgeon.MustacheComponent):
    pass

class PageListing(pydgeon.JinjaComponent):
    pass

class PageFinder(pydgeon.BackboneComponent, pydgeon.JinjaComponent):
    pass

class NVViewer(pydgeon.JinjaComponent):
    pass

class Typeahead(pydgeon.BackboneComponent, pydgeon.JinjaComponent):
    pass

def install(app):
    pydgeon.Component.set_base_dir(os.path.join(app.root_path, "components"))
    pydgeon.register_blueprint(app)
