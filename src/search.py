import models
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


def index(page):
    with open(page.filename) as f:
        content = f.read()

    try:
        et = models.PageIndex.get(models.PageIndex.rowid == page.id)
    except models.PageIndex.DoesNotExist:
        et = None

    if type(content) != unicode:
        content = unicode(content, "utf-8")

    if not et:
        print "INSERTING PAGE INDEX", page.name
        sql = models.PageIndex.insert(
            name=page.name, 
            content=content,
            rowid=page.id)

        sql.execute()

    else:
        print "UPDATING PAGE INDEX", page.name
        et.update(
            name=page.name,
            content=content,
        ).where(models.PageIndex.rowid == page.id).execute()
