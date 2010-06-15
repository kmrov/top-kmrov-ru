# -*- coding: utf-8 -*-
import feedparser
import threading
# import sqlite3
import psycopg2
import math
import sys
import time

def title(entry):
    try:
        if entry.title=='':
            return "<Запись без заголовка>"
        return entry.title
    except AttributeError:
        return "<Запись без заголовка>"

def insertion(entry):
    return (entry.author, entry.link, title(entry), entry.updated, entry.yablogs_links24, entry.yablogs_links24weight, entry.yablogs_comments24, entry.yablogs_commenters24, entry.yablogs_visits24, 0, entry.yablogs_ppb_username, "", "")

'''        for entry in lenta.entries:
            if float(entry.yablogs_links24)>0:
                cur.execute(SQL_INSERT, insertion(entry))'''


SQL_CREATE = "create table yablogs(author text, link text, title text, updated text, links24 real, links24weight real, comments24 real, commenters24 real, visits24 real, rating real, author_name text, txt text, img text)"
SQL_INSERT = "insert into yablogs(author, link, title, updated, links24, links24weight, comments24, commenters24, visits24, rating, author_name, txt, img) values (%s,%s,%s,%s,%s+0.000000001,%s+0.000000001,%s+0.000000001,%s+0.000000001,%s+0.000000001,%s,%s,%s,%s)"
SQL_DELETE = "delete from yablogs"
SQL_SELECT = "select title,link,rating from yablogs order by rating desc limit 20"
SQL_RATING1 = "update yablogs set rating=((3*links24weight/(select max(links24weight) from yablogs))+(comments24/(select max(comments24) from yablogs))+(visits24/(select max(visits24) from yablogs)))"
#SQL_RATING1 = "update yablogs set rating=links24weight*visits24*comments24"
SQL_RATING2 = "update yablogs set rating=rating/4 where (visits24<0.1); update yablogs set rating=rating/4 where (comments24<0.1)"
SQL_RATING3 = "update yablogs set rating=rating/4 where ((links24weight)/(links24))<0.4"
SQL_RATING4 = "update yablogs set rating=rating/6 where (links24weight<0.1)"

def parse(base):
    cur = base.cursor()
    cur.execute(SQL_DELETE)
    i = 0
    while True:
        lenta = feedparser.parse("http://blogs.yandex.ru/entriesapi/?p="+str(i))
        entries = [insertion(entry) for entry in lenta.entries] # if float(entry.yablogs_links24)>0]
        for entry in entries:
            try:
                cur.execute(SQL_INSERT, entry)
                base.commit()
            except psycopg2.IntegrityError:
                base.rollback()
        base.commit()
        i+=1
        if len(lenta.entries)<50:
            break
    cur.execute(SQL_RATING1)
    cur.execute(SQL_RATING2)
    cur.execute(SQL_RATING3)
    cur.execute(SQL_RATING4)
    base.commit()
    cur.execute("select count(*) from yablogs")
    num_entries = int(cur.fetchall()[0][0])
    if num_entries>0:
        cur.execute("delete from top_entry")
        cur.execute("insert into top_entry(author,title,link,rating,links24weight,visits24,comments24) select distinct author,title,link,rating,links24weight,visits24,comments24 from yablogs where links24weight>=2;")
        base.commit()
        cur.execute('insert into top_author(link, "name", icon) select distinct author, author_name, \'icons/loading.gif\' from yablogs where author not in (select link from top_author) and links24weight>=2')
        base.commit()
    cur.close()
    return num_entries

if __name__ == '__main__':
    try:
        import psyco
        psyco.full()
    except:
        pass
    base = psycopg2.connect(host='localhost', user='top', password='top', database='top')
    res = parse(base)
    base.close()
    print ress
