import models
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


def index(page):
    try:
        et = models.PageIndex.get(models.PageIndex.rowid == page.id)
    except models.PageIndex.DoesNotExist:
        et = None

    content = page.text
    if type(content) != unicode:
        content = unicode(page.text, "utf-8")

    if not et:
        sql = models.PageIndex.insert(
            name=page.name, 
            content=content,
            rowid=page.id)

        sql.execute()

    else:
        print "UPDATING PAGE", page.name
        et.update(
            name=page.name,
            content=content,
        ).where(models.PageIndex.rowid == page.id).execute()
