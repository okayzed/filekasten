from peewee import *
from playhouse.sqlite_ext import *
DATABASE="db/wiki.sqlite3"
database = SqliteDatabase(DATABASE)


# model definitions -- the standard "pattern" is to define a base model class
# that specifies which database to use.  then, any subclasses will automatically
# use the correct storage.
class BaseModel(Model):
    class Meta:
        database = database

# the user model specifies its fields (or columns) declaratively, like django
class Page(BaseModel):
    name = CharField(unique=True)
    filename = CharField(unique=True)
    namespace = CharField()

    created = TimestampField()
    updated = TimestampField()

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