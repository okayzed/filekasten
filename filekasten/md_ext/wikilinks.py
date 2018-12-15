from markdown.extensions.wikilinks import WikiLinkExtension
from markdown.extensions.wikilinks import WikiLinks

class WikiLinkExtension(WikiLinkExtension):
    def extendMarkdown(self, md, globals):
        self.md = md

        # append to end of inline patterns
        WIKILINK_RE = r'\[\[([\w0-9_. -]+)\]\]'
        wikilinkPattern = WikiLinks(WIKILINK_RE, self.getConfigs())
        wikilinkPattern.md = md
        md.inlinePatterns.add('wikilink', wikilinkPattern, "<not_strong")
