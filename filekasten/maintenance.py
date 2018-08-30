import config

def find_free_port():
    return config.PORT


from multiprocessing import Value

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

SERVER = None
INDEXER = None
def start_threads(cb):
    global SERVER, INDEXER
    import signal

    from multiprocessing import Process
    signal.signal(signal.SIGINT, signal.SIG_DFL)


    SERVER = Process(target=run_web)
    SERVER.start()

    INDEXER = Process(target=run_indexer)
    INDEXER.start()

    cb()

    INDEXER.terminate()
    INDEXER.join()

    SERVER.terminate()
    SERVER.join()


