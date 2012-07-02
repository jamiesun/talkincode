#!/usr/bin/python2.7 
#coding:utf-8
"""
@description:mysql of python 
"""
import MySQLdb
import uuid
import datetime
from settings import logger

from DBUtils.PooledDB import PooledDB

PUBLIC_KEY = '494ec9f9cbaf40cfa8d4b44447374d27'

dbpool = PooledDB(creator=MySQLdb,
                  maxusage=1000,
                  host='localhost',
                  user='root',
                  passwd='lymysql',
                  db='talkincode_db1',
                  charset="utf8"
                  )

get_conn = lambda : dbpool.connection()

def todict(row,rowdesc):
    d = {}
    for idx, col in enumerate(rowdesc):
        d[col[0]] = row[idx]
    return d


def add_code(title=None,auther=None,email=None,
             tags=None,content=None,lang=None,filename=None,authkey=PUBLIC_KEY):
    # import pdb
    # pdb.set_trace()

    logger.info("add code title=%s,lang=%s"%(title,lang))

    if not authkey:
        logger.error('authkey can not empty')
        raise 'authkey can not empty'

    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("select authkey,hits from authkeys where authkey=%s",(str(authkey)))
        keyobjs = cur.fetchone()
        if not keyobjs:
            logger.error('authkey not exists db')
            raise 'database error'

        authkey_hits = keyobjs[0][1]

        if not content:
            logger.error('content can not empty')
            raise 'content can not empty'


        if not title: title = content[:128].replace('\n','')
        if not auther: auther = 'Anonymous'
        if not email:email = '@'
        if not tags:tags = 'other'
        if not lang:lang="html"
        create_time = datetime.datetime.now().strftime( "%Y-%m-%d %H:%M:%S")
        uid = uuid.uuid4().hex
        cur.execute("insert into codes \
            (id,title,auther,email,tags,content,authkey,lang,filename,create_time)\
             values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
             (uid,title,auther,email,tags,content,authkey,lang,filename,create_time))

        hits = int(authkey_hits) + 1
        cur.execute("update authkeys set hits = %s where authkey=%s",(hits,authkey))
        conn.commit()
    except Exception,e:
        conn.rollback()
        logger.error("database error %s"%e)
        raise
    finally:
        cur.close()
        conn.close()

def list_index(keyword=None,authkey=PUBLIC_KEY,limit=1000):
    if not authkey:
        logger.error('authkey can not empty')
        raise 'authkey can not empty'
        

    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("select authkey,hits from authkeys where authkey=%s",(authkey))
        keyobjs = cur.fetchone()
        if not keyobjs:
            logger.error('authkey not exists db')
            raise 'authkey not exists'

        if keyword:
            sql = "select id,title,auther,email,tags,lang,hits,filename  from codes\
             where title like '%%%s%%' order by create_time desc limit 0,%s"%(keyword,limit)
        else:
            sql = "select id,title,auther,email,tags,lang,hits,filename from codes order by create_time desc limit 0,%s"%limit
        cur.execute(sql)



        result = cur.fetchall()
        return [todict(rt,cur.description) for rt in result]
    except Exception,e:
        logger.error('list_index error %s'%e)
        raise
    finally:
        cur.close()
        conn.close()

def get_content(uid,authkey=PUBLIC_KEY):
    if not authkey:
        raise 'authkey can not empty'
    if not uid :
        raise 'id can not empty'


    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("select authkey,hits from authkeys where authkey=%s",(authkey))
        keyobjs = cur.fetchone()
        if not keyobjs:
            raise 'authkey not exists'

        cur.execute("select hits from codes where id=%s",(uid))
        codeobjs = cur.fetchone()            
        print codeobjs
        code_hits = codeobjs[0]
        hits = (int(code_hits) + 1)
        
        cur.execute("update codes set hits = %s where id=%s",(hits,uid))
        conn.commit()            
        cur.execute("select title,content from codes where id = %s",uid)
        ones =  cur.fetchone()
        if ones :
            return todict(ones,cur.description)
        else:
            return 'no result'
    except:
        raise
    finally:
        cur.close()
        conn.close()




if __name__ == "__main__":
    result = list_index(limit=50)
    import json
    print result
    print json.dumps(result)

    print get_content('059e2d49a7164a37b499b6da1d189be1',PUBLIC_KEY)
