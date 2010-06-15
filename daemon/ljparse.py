import psycopg2
import urllib2
import httplib
import re
import os.path
from cStringIO import StringIO
from PIL import Image
import psycopg2
import feedparser
import autorss
import socket
from urlparse import urljoin
import sys

# TEXT_RE = r"<font face='Arial,Helvetica' size='\+1'><i><b>.*?<\/b><\/i><\/font><br \/>(.*?)<\/div><br style='clear: both' \/><hr width='100%' size='2' align='center' \/><div id='Comments'><a name='comments'><\/a>"

TEXT_RE = r"""(?s)<img src="http://l-stat.livejournal.com/img/btn_next.gif" width="22" height="20" alt="Next Entry" title="Next Entry" border='0' align="absmiddle" /></a></td></tr></table>\n<hr />\n</blockquote>\n<div style='margin-left: 30px'>(?:<table border=0>\n?.*?\n?.*?\n?</table><p>\n)?(?:<font face='Arial,Helvetica' size='\+1'><i><b>.*?<\/b><\/i><\/font><br \/>\n)?(?P<text>.*?)<\/div><br style='clear: both' \/><hr width='100%' size='2' align='center' \/>(?:\n\s*<div class="adv">|<div id='Comments'><a name='comments'><\/a>)?"""

MEDIA_ROOT = '/home/winnukem/top/top_webapp/media/'
IMGPATH = 'cache'

def get_rss_link(link):
    if link.find('livejournal.com')==-1:
        req = urllib2.urlopen(link, timeout=15)
        text = req.read()
        rss_link = re.search(r'<link.*?type=.?application\/rss\+xml.*?href="(?P<href>.*?)".*?>', text).group("href").lstrip().rstrip()
        if rss_link.find('http://')==-1:
            rss_link = urljoin(link, rss_link)
        return rss_link
    else:
        return link + "data/rss"

def fetch_from_rss(link, author):
    try:
        rss_link = get_rss_link(author)
        link_parts = [s for s in link.split("/") if s!='']
        link_id = link_parts[-1]
        lenta = feedparser.parse(rss_link)
        for entry in lenta.entries:
            entry_parts = [s for s in entry.link.split("/") if s!='']
            entry_id = entry_parts[-1]
            if entry_id==link_id:
                return entry.summary
    except:
        return None

def fetch_from_livejournal(link):
    if link.find('livejournal.com')==-1:
        return None
    link2 = link + '?format=light'
    req = urllib2.Request(link2)
    req.add_header("Cookie", "adult_concepts=1; adult_explicit=1")
    req.add_header("User-agent", "kmrov.ru bot (nikita@kmrov.ru)")
    try:
        f = urllib2.urlopen(req, timeout=15)
        text = f.read()
    except (urllib2.URLError, httplib.IncompleteRead, socket.timeout):
        return None
    try:
        text = re.search(TEXT_RE, text).group("text").lstrip().rstrip()
    except AttributeError:
        return None
    return text    

def fetch_image(text, filename, link):
    try:
        imgs = re.findall(r'<img\s.*?src=\"(.*?)\"(?:.*?)>', text)
    except AttributeError:
        return None
    fname = ""
    for src in imgs:
        try:
            imgdata = urllib2.urlopen(src, timeout=15)
            imgfile = StringIO()
            imgfile.write(imgdata.read())
        except Exception as ex: #(urllib2.URLError, httplib.IncompleteRead, ValueError, socket.timeout, httplib.InvalidURL):
            print link + "\nexception: " + str(ex)
            continue
        imgfile.seek(0)
        try:
            im = Image.open(imgfile)
        except IOError:
            print "exception"
            continue
        if im.size[0]>64 and im.size[1]>64:
            try:
                if im.size[0]>im.size[1]:
                    im2 = im.resize((160, int(160*(float(im.size[1])/float(im.size[0])))), Image.ANTIALIAS)
                else:
                    im2 = im.resize((int(160*(float(im.size[0])/float(im.size[1]))), 160), Image.ANTIALIAS)
                fname = os.path.join(IMGPATH, filename + "." + str.lower(im.format))
                im2.save(os.path.join(MEDIA_ROOT, fname))
                return fname
            except IOError:
                print "exception"
                fname = ""
                continue                    
            break

def process(row, cur, base):
    retags = re.compile(r'(?s)<.*?>')
    rebr = re.compile(r'((<br.*?>\s*)+)|((<\/?p.*?>\s*)+)')
    relines = re.compile(r'\n(?:\n|\s)*')
    reempty = re.compile(r'^(?:\n|\s)+$')
    link = row[1]
    author = row[2]
    print link
#    print link
#    cur.execute("select link from top_cached_entry where link=%s", (link,))
#    if len(cur.fetchall())>0:
#        print "skipped"
#        return
    text = fetch_from_rss(link, author)
    if (text==None or text=="") and link.find('livejournal.com')!=-1:
        text = fetch_from_livejournal(link)
    if text==None:
        text = ""
    fname = ""
    if text!="":
        filename = link.replace("http://", '').replace('/', '-').replace('?','-').replace('&', '-')
        fname = fetch_image(text, filename, link)
    text = text.replace('&nbsp;', ' ')
    text = rebr.sub('\n', text)
    text = retags.sub('', text)
    text = relines.sub('\n', text)
    text = reempty.sub('', text)
    text = text.replace('\n', '<br>')
    if text.startswith('<br>'):
        text = text[4:]
    cur.execute("insert into top_cached_entry(link, txt, image) values(%s, %s, %s)", (link, text, fname))
    base.commit()

def parse(base):
    feedparser.USER_AGENT = "kmrov.ru bot (nikita@kmrov.ru)"
    cur = base.cursor()
    cur.execute("select distinct title,link,author,rating from top_entry where link not in (select link from top_cached_entry) order by rating desc")
    rows = cur.fetchall()
    for row in rows:
        process(row, cur, base)
        sys.stdout.flush()
        os.fsync(sys.stdout.fileno())
    cur.close()
    return "ok"

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
    print res
