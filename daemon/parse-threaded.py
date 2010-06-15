import feedparser
import threading
import sqlite3
import math
import Queue

def rating(entry):
    return 160*float(entry.yablogs_links24weight) + \
        20*math.sqrt(float(entry.yablogs_comments24)*float(entry.yablogs_commenters24)) + \
        float(entry.yablogs_visits24)

def title(entry):
    try:
        return entry.title
    except AttributeError:
        return "##no title##"

page = 0
pagelock = threading.Lock()
finished = False

class ParserThread(threading.Thread):
    def run(self):
        global page
        global results
        global finished
        while finished==False:
            pagelock.acquire()
            current_page = page
            page += 1
            pagelock.release()
            print str(current_page) + " started"
            lenta = feedparser.parse("http://blogs.yandex.ru/entriesapi/?p="+str(current_page))
            for entry in lenta.entries:
                base.execute("insert into yablogs(author, link, title, updated, links24weight, comments24, commenters24, visits24, rating) values (?,?,?,?,?,?,?,?,?)", (entry.author, entry.link, title(entry), entry.updated, entry.yablogs_links24weight, entry.yablogs_comments24, entry.yablogs_commenters24, entry.yablogs_visits24, rating(entry)))
            
            print str(current_page) + " finished"
            if len(lenta.entries)<50:
                finished = True
        print "SAVSEM FINISHED"

base = sqlite3.connect("base.db")
base.execute("create table yablogs(author, link, title, updated, links24weight, comments24, commenters24, visits24, rating)")

# while finished==False:
for i in xrange(10):
    ParserThread().start()

while finished==False:
    pass

base.commit()

print "finished fuck yeah"

'''
i = 0
while True:
    i+=1
    try:
        lenta = results.get()
    except:
        print "queue empty"
        break
    print "adding " + str(i)
    for entry in lenta.entries:
        base.execute("insert into yablogs(author, link, title, updated, links24weight, comments24, commenters24, visits24, rating) values (?,?,?,?,?,?,?,?,?)", (entry.author, entry.link, title(entry), entry.updated, entry.yablogs_links24weight, entry.yablogs_comments24, entry.yablogs_commenters24, entry.yablogs_visits24, rating(entry)))
    print "added " + str(i)
    base.commit()
print "finished adding to db"
base.commit()
print "commited"


while True:
    lenta = feedparser.parse("http://blogs.yandex.ru/entriesapi/?p="+str(i))
    for entry in lenta.entries:
        base.execute("insert into yablogs(author, link, title, updated, links24weight, comments24, commenters24, visits24, rating) values (?,?,?,?,?,?,?,?,?)", (entry.author, entry.link, title(entry), entry.updated, entry.yablogs_links24weight, entry.yablogs_comments24, entry.yablogs_commenters24, entry.yablogs_visits24, rating(entry)))
    i+=1
    if len(lenta.entries)<50:
        break
print i
base.commit() '''
