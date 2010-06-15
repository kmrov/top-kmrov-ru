from django.db import models
from django.db import connection

req = '''
SELECT * 
 FROM 
    top_entry 
    LEFT OUTER JOIN top_cached_entry 
        ON top_entry.link=top_cached_entry.link
    LEFT OUTER JOIN top_author
        ON top_entry.author=top_author.link
 WHERE top_entry.link NOT IN (SELECT txt FROM top_exclusion WHERE openid='http://winnukem.livejournal.com/' AND what=1)
   AND top_entry.author NOT IN (SELECT txt FROM top_exclusion WHERE openid='http://winnukem.livejournal.com/' AND what=0)
 ORDER BY rating DESC
 LIMIT 50;
'''

class entry_manager(models.Manager):
    def excluded(self, openid):
        cursor = connection.cursor()
        cursor.execute('''select e.author,e.title,e.link,e.rating,e.links24weight,
                                 e.visits24,e.comments24, c.txt, c.image, a.name, a.icon
                          from 
                          top_exclusion ex
                          inner join top_entry e
                          on e.link=ex.txt
                          inner join top_author a
                          on a.link=e.author
                          inner join top_cached_entry c
                          on c.link=ex.txt
                          where ex.what=1 and openid=%s''', (openid,))
        result_list = []
        for row in cursor.fetchall():
            p = self.model(author=row[0], title=row[1], link=row[2], rating=row[3], links24weight=row[4],
                           visits24=row[5], comments24=row[6])
            p.cached_entry = cached_entry(link=row[2], txt=row[7], image=row[8])
            p.cached_author = author(link=row[0], name=row[9], icon=row[10])
            result_list.append(p)
        return result_list
        
        
    def filtered(self, openid=''):
        cursor = connection.cursor()
        if not openid=='':
            cursor.execute('''SELECT e.author,e.title,e.link,e.rating,e.links24weight,
                                 e.visits24,e.comments24, c.txt, c.image, a.name, a.icon
                             FROM 
                                top_entry e
                                LEFT OUTER JOIN top_cached_entry c
                                    ON e.link=c.link
                                LEFT OUTER JOIN top_author a
                                    ON e.author=a.link
                             WHERE e.link NOT IN (SELECT txt FROM top_exclusion WHERE openid=%s AND what=1)
                               AND e.author NOT IN (SELECT txt FROM top_exclusion WHERE openid=%s AND what=0)
                             ORDER BY rating DESC
                             LIMIT 50;''', (openid, openid))
        else:
            cursor.execute('''SELECT e.author,e.title,e.link,e.rating,e.links24weight,
                                 e.visits24,e.comments24, c.txt, c.image, a.name, a.icon
                             FROM 
                                top_entry e
                                LEFT OUTER JOIN top_cached_entry c
                                    ON e.link=c.link
                                LEFT OUTER JOIN top_author a
                                    ON e.author=a.link
                             ORDER BY rating DESC
                             LIMIT 50;''')
        result_list = []
        for row in cursor.fetchall():
            p = self.model(author=row[0], title=row[1], link=row[2], rating=row[3], links24weight=row[4],
                           visits24=row[5], comments24=row[6])
            p.cached_entry = cached_entry(link=row[2], txt=row[7], image=row[8])
            p.cached_author = author(link=row[0], name=row[9], icon=row[10])
            result_list.append(p)
        return result_list

class entry(models.Model):
    author = models.CharField(max_length=256)
    title = models.CharField(max_length=512)
    link = models.URLField(primary_key = True)
    rating = models.FloatField()
    links24weight = models.FloatField()
    visits24 = models.FloatField()
    comments24 = models.FloatField()
    objects = entry_manager()
    def get_cache(self):
        try:
            return self.cached_entry
        except AttributeError:
            self.cached_entry=cached_entry.objects.get(link = self.link)
            return self.cached_entry
    def get_author(self):
        try:
            return self.cached_author
        except AttributeError:
            self.cached_author=author.objects.get(link = self.author)
            return self.cached_author

class cached_entry(models.Model):
    link = models.URLField(primary_key = True)
    txt = models.TextField()
    image = models.ImageField(upload_to='cache')

class exclusion(models.Model):
 #   WHAT_CHOICES = ((0, "author"),(1,"link"))
    what = models.IntegerField()
    txt = models.CharField(max_length=256)
    openid = models.CharField(max_length=256)
    class Meta:
        ordering = ('txt', )
    def get_author(self):
        if self.what==0:
            try:
                return self.cached_author
            except AttributeError:                
                self.cached_author = author.objects.get(link = self.txt)
                return self.cached_author
        else:
            return None

class author_manager(models.Manager):
    def excluded(self, openid):
        cursor = connection.cursor()
        cursor.execute('''select a.id, a.link, a.name, a.icon from 
                          top_exclusion e
                          inner join top_author a
                          on a.link=e.txt
                          where e.what=0 and e.openid=%s
                          order by a.link''', (openid,))
        authors = []
        for row in cursor.fetchall():
            p = self.model(id=row[0], link=row[1], name=row[2], icon=row[3])
            authors.append(p)
        return authors

class author(models.Model):
    link = models.CharField(max_length=256)
    name = models.CharField(max_length=512)
    icon = models.ImageField(upload_to='icons')
    objects = author_manager()
