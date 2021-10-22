import sys
import os

import threading
import signal
import subprocess

import gi
gi.require_version('WebKit2', '4.0')
from gi.repository import Gtk, WebKit2

from . import config

WIKI_URL = "http://localhost:32333/"
DEFAULT_URL="http://localhost:32333/wiki"
class Browser(Gtk.Window):
    def __init__(self, *args, **kwargs):
        super(Browser, self).__init__(*args, **kwargs)

        self.connect("destroy", Gtk.main_quit)
        self.set_size_request(1200,700)

        self.webview = WebKit2.WebView()

        settings = self.webview.get_settings()
        settings.set_property("enable-java-applet", False)
        settings.set_property("enable-plugins", False)

        self.webview.connect("navigation-policy-decision-requested", self.navigate)
        self.webview.load_uri(DEFAULT_URL)

        self.add(self.webview)
        self.show_all()

    def navigate(self, view, frame, request, action, decision):
        uri = request.get_uri()
        print("URI", uri)
        if (uri.startswith(WIKI_URL)):
            return False
        else:
            decision.ignore()
            uri = request.get_uri()
            subprocess.call(["xdg-open", uri])
            return True
        return False




class Inspector(Gtk.Window):
    def __init__(self, view, *args, **kwargs):
        super(Inspector, self).__init__(*args, **kwargs)
        self.set_size_request(1200,700)
        self.webview = view
        settings = WebKit2.WebSettings()
        settings.set_property('enable-developer-extras', True)
        view.set_settings(settings)


        self.webview = WebKit2.WebView()
        self.inspector = view.get_inspector()

        self.inspector.connect("inspect-web-view", self.inspect)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.add(self.scrolled_window)
        self.scrolled_window.show()

        self.webview = WebKit2.WebView()
        self.scrolled_window.add(self.webview)

    def inspect(self,inspector,view,*a,**kw):
        self.scrolled_window.show_all()
        self.show()
        return self.webview


from . import maintenance
def run_browser():
    def run_gtk_browser():
        Gtk.init(sys.argv)
        browser = Browser()
        inspector = Inspector(browser.webview)


        Gtk.main()

    maintenance.start_threads(run_gtk_browser)


if __name__ == "__main__":
    run_browser()

