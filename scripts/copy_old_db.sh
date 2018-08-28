# make a copy of old.db
# cp db/wiki.sqlite3 db/wiki.sqlite3.bak

# remove and recreate the DB

# in sqlite3
# attach database "./db/wiki.sqlite3.bak" as oldwiki
# insert into main.page select * from oldwiki.page
# insert into main.pageindex select * from oldwiki.pageindex
