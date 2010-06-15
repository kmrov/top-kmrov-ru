import psycopg2
import re
from cStringIO import StringIO
import urllib2
from urlparse import urljoin
import os.path
from ljparse import get_rss_link
import feedparser
from PIL import Image

MEDIA_ROOT = '/home/winnukem/top/top_webapp/media/'

def parse(base):
    cur = base.cursor()
    cur.execute("select link from top_author where icon='icons/loading.gif'")
    rows = cur.fetchall()
    authors = list(set([row[0] for row in rows]))
    for author in authors:
        icon = ""
        if author.find('livejournal.com')!=-1:
            if author.startswith("http://users.livejournal.com"):
                icon = 'icons/lj_user.gif'
            elif author.startswith("http://community.livejournal.com"):
                icon = 'icons/lj_comm.gif'
            else:
                icon = 'icons/lj_user.gif'
        elif author.find('.mail.ru')!=-1:
            icon = 'icons/mailru.gif'
        elif author.find('friendfeed.com')!=-1:
            icon = 'icons/friendfeed.gif'
        else:
            if author.find("liveinternet.ru")!=-1:
                icon = 'icons/liru.gif'
            elif author.find(".blog.ru")!=-1:
                icon = 'icons/blogru.gif'
            elif author.find(".ya.ru")!=-1:
                icon = 'icons/yaru.gif'
            elif author.find("blogspot.com")!=-1:
                icon = 'icons/blogger.gif'
            elif author.find('twitter.com')!=-1:
                icon = 'icons/twitter.gif'
            elif author.find('lj.rossia.org')!=-1:
                icon = 'icons/rossia.gif'
            else:
                src = urljoin(author, "/favicon.ico")
                try:
                    filename = urljoin(author, '/').replace('http://', '').replace('/', '') + '.png'
                    filename = os.path.join('icons', filename)
                    if os.path.exists(os.path.join(MEDIA_ROOT, filename)):
                        icon = filename
                    else:
                        imgdata = urllib2.urlopen(src, timeout=15)
                        imgfile = StringIO()
                        imgfile.write(imgdata.read())
                        imgfile.seek(0)
                        im = Image.open(imgfile)
                        im.save(os.path.join(MEDIA_ROOT, filename), "PNG")
                        icon = filename
                except Exception as ex:
                    icon = 'icons/empty.gif'
                    print author + ": " + str(ex)
        print author + " : " + icon
        cur.execute("update top_author set icon=%s where link=%s", (icon, author))
        base.commit()
    cur.close()
    return 0

if __name__ == '__main__':
    try:
        import psyco
        psyco.full()
    except:
        pass
    base = psycopg2.connect(host='localhost', user='top', password='top', database='top')
    res = parse(base)
    base.commit()
    base.close()
#    print res
