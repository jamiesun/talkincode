#!/usr/bin/python2.7 
#coding:utf-8
from settings import logger
from store import get_conn,todict,doauthkey
import uuid
import datetime



def list_langs():
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("select name,hits from langs order by hits desc")
        result = cur.fetchall()
        return [todict(rt,cur.description) for rt in result]
    except Exception,e:
        logger.error('list_langs error %s'%e)
        raise
    finally:
        cur.close()
        conn.close()

@doauthkey
def add_code(pid=0,title=None,auther=None,email=None, tags=None,
             content=None,lang=None,filename=None,authkey=None):
    logger.info("add code title=%s,lang=%s"%(title,lang))
    conn = get_conn()
    cur = conn.cursor()
    try:
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
            (id,parent,title,auther,email,tags,content,authkey,lang,filename,create_time)\
             values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
             (uid,pid,title,auther,email,tags,content,authkey,lang,filename,create_time))
        conn.commit()
    except Exception,e:
        conn.rollback()
        logger.error("database error %s"%e)
        raise
    finally:
        cur.close()
        conn.close()

@doauthkey
def list_index(keyword=None,limit=1000,authkey=None):
    conn = get_conn()
    cur = conn.cursor()
    try:
        if keyword:
            sql = "select id,title,auther,email,tags,lang,hits,filename,create_time from codes\
             where title like '%%%s%%' order by create_time desc limit 0,%s"%(keyword,limit)
        else:
            sql = "select id,title,auther,email,tags,lang,hits,filename,create_time\
             from codes order by create_time desc limit 0,%s"%limit
        cur.execute(sql)

        result = cur.fetchall()
        return [todict(rt,cur.description) for rt in result]
    except Exception,e:
        logger.error('list_index error %s'%e)
        raise
    finally:
        cur.close()
        conn.close()

@doauthkey
def get_content(uid,authkey=None):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("select hits from codes where id=%s",(uid))
        codeobjs = cur.fetchone()   

        if not codeobjs:
            raise Exception('code not exists')         

        code_hits = codeobjs[0]
        hits = (int(code_hits) + 1)
        
        cur.execute("update codes set hits = %s where id=%s",(hits,uid))
        conn.commit()            
        cur.execute("select title,auther,tags,lang,content,hits,create_time\
         from codes where id = %s",uid)
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

    print get_content('059e2d49a7164a37b499b6da1d189be1')