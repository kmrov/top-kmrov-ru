#!/usr/bin/env python

import sys, time
from daemon import Daemon
from yaparse import parse as yaparse
from ljparse import parse as ljparse
from authorparse import parse as authorparse
import psycopg2
import os

import time

#import pdb

BASE = '/home/winnukem/top/daemon/base.db'

try:
    import psyco
    psyco.full()
except:
    pass

class TopDaemon(Daemon):
    def sync(self):
        sys.stdout.flush()
        os.fsync(sys.stdout.fileno())
        
    def run(self):
#        pdb.set_trace()
        while True:
            try:
                print time.ctime() + ": parsing started"
                self.sync()
                self.base = psycopg2.connect(host='localhost', user='top', password='top', database='top')
                yaparse(self.base)
                authorparse(self.base)
                ljparse(self.base)
                print time.ctime() + ": parsing finished"
                self.sync()
                self.base.close()
                time.sleep(360)
            except (psycopg2.ProgrammingError, psycopg2.DatabaseError, psycopg2.IntegrityError, psycopg2.InternalError) as ex:
                print str(ex)
                self.base.rollback()
                self.base.close()
                continue
            except Exception as ex:
                print str(ex)
                self.base.close()
                continue

'''
class LjDaemon(Daemon):
    def run(self):
        base = psycopg2.connect(host='localhost', user='top', password='top', database='top')
        while True:
            ljparse(base)
            time.sleep(1800)
        base.close()
'''
if __name__ == "__main__":
	daemon = TopDaemon('/tmp/top-daemon.pid', '/dev/null', '/home/winnukem/top/top-out.log', '/home/winnukem/top/top-err.log')
	if len(sys.argv) == 2:
		if 'start' == sys.argv[1]:
			daemon.start()
		elif 'stop' == sys.argv[1]:
			daemon.stop()
		elif 'restart' == sys.argv[1]:
			daemon.restart()
		else:
			print "Unknown command"
			sys.exit(2)
		sys.exit(0)
	else:
		print "usage: %s start|stop|restart" % sys.argv[0]
		sys.exit(2)
