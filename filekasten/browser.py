import sys
import os 

import threading
import signal

import gi
from gi.repository import Gtk, WebKit


DEFAULT_URL="http://localhost:5000/wiki"
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

import socket
from contextlib import closing

def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        return s.getsockname()[1]


SERVER = None
def run_web():
    import web
    global DEFAULT_URL, SERVER

    open_port = find_free_port()
    DEFAULT_URL="http://localhost:%s/wiki" % open_port

    from multiprocessing import Process

    SERVER = Process(target=web.app.run, kwargs={ "port" : open_port })
    SERVER.start()

    print "SERVER IS", SERVER

def run_browser():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    run_web()

    Gtk.init(sys.argv)
    browser = Browser()

    Gtk.main()

    SERVER.terminate()
    SERVER.join()

if __name__ == "__main__":
    run_browser()

