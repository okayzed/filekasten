import sys
import os

import threading
import signal

import gi
from gi.repository import Gtk, WebKit

import config

DEFAULT_URL="http://localhost:32333/wiki"
class Browser(Gtk.Window):
    def __init__(self, *args, **kwargs):
        super(Browser, self).__init__(*args, **kwargs)

        self.connect("destroy", Gtk.main_quit)
        self.set_size_request(1200,700)

        self.webview = WebKit.WebView()

        settings = self.webview.get_settings()
        settings.set_property("enable-java-applet", False)
        settings.set_property("enable-plugins", False)

	self.webview.load_uri(DEFAULT_URL)

        self.add(self.webview)
        self.show_all()

class Inspector(Gtk.Window):
    def __init__(self, view, *args, **kwargs):
        super(Inspector, self).__init__(*args, **kwargs)
        self.set_size_request(1200,700)
        self.webview = view
        settings = WebKit.WebSettings()
        settings.set_property('enable-developer-extras', True)
        view.set_settings(settings)


        self.webview = WebKit.WebView()
        self.inspector = view.get_inspector()

        self.inspector.connect("inspect-web-view", self.inspect)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.add(self.scrolled_window)
        self.scrolled_window.show()

        self.webview = WebKit.WebView()
        self.scrolled_window.add(self.webview)

    def inspect(self,inspector,view,*a,**kw):
        self.scrolled_window.show_all()
        self.show()
        return self.webview


import maintenance
def run_browser():
    def run_gtk_browser():
        Gtk.init(sys.argv)
        browser = Browser()
	inspector = Inspector(browser.webview)


        Gtk.main()

    maintenance.start_threads(run_gtk_browser)


if __name__ == "__main__":
    run_browser()

