"""
List that supports 'x' mark at beginning
=======================================
"""

from __future__ import absolute_import
from __future__ import unicode_literals
from markdown import Extension
from markdown.preprocessors import Preprocessor
from markdown.blockprocessors import OListProcessor, UListProcessor
import re

MYREGEX = re.compile(r'^([ ]{0,4})[x][ ]+(.*)')
SECONDREGEX = re.compile(r'^([ ]{0,4})[*] \[x\][ ]+(.*)')
class XUListProcessor(Preprocessor):
    def run(self, lines):
        new_lines = []
        for line in lines:
            m = MYREGEX.match(line)
            if m:
                space = m.group(1)
                line = "%s* <s class='strikethrough'>%s</s>" % (space, line)

            m = SECONDREGEX.match(line)
            if m:
                space = m.group(1)
                line = "%s* <s class='strikethrough'>%s</s>" % (space, line.strip("* "))

            new_lines.append(line)
        return new_lines


class XListExtension(Extension):
    def extendMarkdown(self, md, md_global):
        """ Override existing Processors. """
        md.preprocessors['xlist'] = XUListProcessor(md.parser)



def makeExtension(**kwargs):  # pragma: no cover
    return XListExtension(**kwargs)
