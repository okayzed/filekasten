import argparse
import os
import time
import frontmatter

from . import models

def clean_missing_files():
    pages = models.Page.select().execute();
    for page in pages:
        if page.filename:
            if not os.path.exists(page.filename):
                print("DELETING PAGE", page.name)
                page.delete().where(models.Page.filename == page.filename).execute()

if __name__ == "__main__":
    clean_missing_files()
