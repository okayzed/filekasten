import sys
import os

import threading
import signal

import gi
from gi.repository import Gtk, WebKit

import config

from multiprocessing import Value

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

import socket
from contextlib import closing

def find_free_port():
    return config.PORT

INDEXING=Value('b', True)
INDEX_INTERVAL=60
EXPORT_INTERVAL=60*60
import time

import ingest_flat_files, exgest_flat_files, clean_missing_files
def do_index():
    clean_missing_files.clean_missing_files()
    ingest_flat_files.ingest_files(config.DIRS, config.JOURNAL, config.HIDDEN)

def do_export():
    exgest_flat_files.export_files_to_dir(config.BACKUP_DIR)

def run_indexer():
    last_export = time.time() - 1
    last_index = time.time() - 1
    import config
    while INDEXING.value:
        time.sleep(1)
        reload(config)
        print "CHECKING", INDEXING.value

        now = time.time()

        if now - last_index > INDEX_INTERVAL:
            do_index()
            # do some ingestion
            last_index = now

        if now - last_export > EXPORT_INTERVAL:
            do_export()
            last_export = now

    print "DONE INDEXING"

def run_web():
    import web
    global DEFAULT_URL, INDEXING
    open_port = find_free_port()
    DEFAULT_URL="http://localhost:%s/wiki" % open_port

    try:
        web.app.run(port=open_port)
    finally:
        INDEXING.value = False
        print "SET", INDEXING.value


SERVER = None
INDEXER = None
def start_threads():
    global SERVER, INDEXER

    from multiprocessing import Process

    SERVER = Process(target=run_web)
    SERVER.start()

    INDEXER = Process(target=run_indexer)
    INDEXER.start()

    Gtk.init(sys.argv)
    browser = Browser()

    Gtk.main()

    INDEXER.terminate()
    INDEXER.join()

    SERVER.terminate()
    SERVER.join()

def run_browser():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    start_threads()


if __name__ == "__main__":
    run_browser()

