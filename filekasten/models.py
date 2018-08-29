import os

from peewee import *
from playhouse.sqlite_ext import *

from config import FILEKASTEN_DIR
DATABASE=os.path.join(FILEKASTEN_DIR, "db/wiki.sqlite3")
database = SqliteDatabase(DATABASE, pragmas={
  'journal_mode': 'wal',
})


# model definitions -- the standard "pattern" is to define a base model class
# that specifies which database to use.  then, any subclasses will automatically
# use the correct storage.
class BaseModel(Model):
    class Meta:
        database = database

# the user model specifies its fields (or columns) declaratively, like django
class Page(BaseModel):
    name = CharField()
    filename = CharField(unique=True)
    namespace = CharField()

    journal = BooleanField(index=True)
    hidden = BooleanField(index=True)

    created = TimestampField(index=True)
    updated = TimestampField(index=True)

    class Meta:
        indexes = (
            (('namespace', 'name'), True),
        )
        # create a unique on from/to/date


class PageIndex(FTSModel):
    rowid = RowIDField()
    name = SearchField()
    content = SearchField()

    class Meta:
        database = database
        options =  { "tokenize" : "porter" }

def create_tables():
    with database:
        database.create_tables([Page, PageIndex])

if __name__ == "__main__":
    create_tables()
