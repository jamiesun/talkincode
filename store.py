#!/usr/bin/python2.7 
#coding:utf-8
"""
@description:mysql of python 
"""
import MySQLdb

from DBUtils.PooledDB import PooledDB

dbpool = PooledDB(creator=MySQLdb,
                  maxusage=1000,
                  host='localhost',
                  user='root',
                  passwd='root',
                  db='talkincode_db1',
                  charset="utf8"
                  )

get_conn = lambda : dbpool.connection()

def todict(row,rowdesc):
    d = {}
    for idx, col in enumerate(rowdesc):
        d[col[0]] = row[idx]
    return d

def get_option(key,default=None):
    if not key:
        return None
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("select value from settings where key=%s",key)
        robj = cur.fetchone()
        if not robj:
            return default
        else:
            return robj[0]
    except Exception, e:
        raise e
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    conn = get_conn()
    cur = conn.cursor()
    grps = ["C&c++编程","java编程","python编程","php编程","sublime text 2小站","vim小站","emacs小站"]
    langs = "c,c++,java,c#,python,ruby,php,perl,objective-c,vb,javascript, pascal,Lisp,sql,ada,lua,matlab,shell,go"
    langarray = langs.split(",")
    try:
        cur.execute("delete from langs")
        for la in langarray:
            cur.execute("insert into langs (name,hits) values(%s,%s)",(la,0))
        cur.execute("delete from groups")
        for g in grps:
            cur.execute("insert into groups (name,posts) values(%s,%s)",(g,0))        
        conn.commit()
    except Exception, e:
        raise e
    finally:
        cur.close()
        conn.close()


