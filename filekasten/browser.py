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

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.add(self.webview)
        self.add(scrolled_window)
        scrolled_window.show_all()

        self.show()

import maintenance
def run_browser():
    def run_gtk_browser():
        Gtk.init(sys.argv)
        browser = Browser()

        Gtk.main()

    maintenance.start_threads(run_gtk_browser)


if __name__ == "__main__":
    run_browser()
