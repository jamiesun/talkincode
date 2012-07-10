#!/usr/bin/python2.7 
#coding:utf-8
from settings import logger,pagesize,cache
from store import get_conn,todict
import uuid
import datetime
import web

@cache.cache('list_langs_func', expire=3600)
def list_langs():
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("select name,ext,hits from langs order by hits desc")
        if web.config.debug:
            logger.info("execute sql: %s "%cur._executed)        
        result = cur.fetchall()
        return [todict(rt,cur.description) for rt in result]
    except Exception,e:
        logger.error('list_langs error %s'%e)
        raise
    finally:
        cur.close()
        conn.close()

def add_code(pid=0,title=None,author=None,email=None, tags=None,
             content=None,lang=None,filename=None,authkey=None,via=None):
    logger.info("add code title=%s,lang=%s"%(title,lang))
    conn = get_conn()
    cur = conn.cursor()
    try:
        if not content:
            logger.error('content can not empty')
            raise 'content can not empty'

        if not title: title = content[:128].replace('\n','')
        if not author: author = 'Anonymous'
        if not email:email = '@'
        if not tags:tags = 'other'
        if not lang:lang="html"
        create_time = datetime.datetime.now().strftime( "%Y-%m-%d %H:%M:%S")
        uid = uuid.uuid4().hex
        cur.execute("insert into codes \
            (id,parent,title,author,email,tags,content,authkey,lang,filename,create_time,via)\
             values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
             (uid,pid,title,author,email,tags,content,authkey,lang,filename,create_time,via))
        if web.config.debug:
            logger.info("execute sql: %s "%cur._executed)        
        conn.commit()
    except Exception,e:
        conn.rollback()
        logger.error("database error %s"%e)
        raise
    finally:
        cur.close()
        conn.close()


def list_index(keyword=None,page=1,limit=pagesize):
    conn = get_conn()
    cur = conn.cursor()
    offset = 0
    if page >= 1:
        offset = (page -1) * limit    
    try:
        if keyword:
            sql = "select id,title,author,email,tags,lang,hits,filename,create_time,via from codes\
             where title like '%%%s%%' order by create_time desc limit %s,%s"%(keyword,offset,limit)
        else:
            sql = "select id,title,author,email,tags,lang,hits,filename,create_time\
             from codes order by create_time desc limit %s,%s"%(offset,limit)
        cur.execute(sql)
        if web.config.debug:
            logger.info("execute sql: %s "%cur._executed)
        result = cur.fetchall()
        return [todict(rt,cur.description) for rt in result]
    except Exception,e:
        logger.error('list_index error %s'%e)
        raise
    finally:
        cur.close()
        conn.close()

def list_codes_bylang(lang,page=1,limit=pagesize):
    conn = get_conn()
    cur = conn.cursor()
    offset = 0
    if page >= 1:
        offset = (page -1) * limit
    try:
        cur.execute("""SELECT id,title,author,email,tags,lang,hits,filename,create_time,via
                        FROM codes
                        WHERE lang = %s
                        order by create_time desc limit %s,%s""",(lang,offset,limit))
        if web.config.debug:
            logger.info("execute sql: %s "%cur._executed)
        result = cur.fetchall()
        return [todict(rt,cur.description) for rt in result]
    except Exception,e:
        logger.error('list_index error %s'%e)
        raise
    finally:
        cur.close()
        conn.close()      

def list_codes_bytags(tag,page=1,limit=pagesize):
    conn = get_conn()
    cur = conn.cursor()
    offset = 0
    if page >= 1:
        offset = (page -1) * limit
    try:
        cur.execute("""SELECT id,title,author,email,tags,lang,hits,filename,create_time,via
                        FROM codes 
                        WHERE tags like %s
                        order by id desc limit %s,%s""",('%%%s%%'%tag,offset,limit))
        if web.config.debug:
            logger.info("execute sql: %s "%cur._executed)
        result = cur.fetchall()
        return [todict(rt,cur.description) for rt in result]
    except Exception,e:
        logger.error('list_index error %s'%e)
        raise
    finally:
        cur.close()
        conn.close()              

def list_versions(pid,limit=pagesize):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""select id,parent,title,author,email,tags,lang,hits,filename,create_time,via
         from codes where parent = %s
         order by create_time desc limit 0,%s""",(pid,limit))
        if web.config.debug:
            logger.info("execute sql: %s "%cur._executed)        
        result = cur.fetchall()
        return [todict(rt,cur.description) for rt in result]
    except Exception,e:
        logger.error('list_index error %s'%e)
        raise
    finally:
        cur.close()
        conn.close()        

@cache.cache('code_get_content_func', expire=3600)
def get_content(uid):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("select hits from codes where id=%s",(uid))
        codeobjs = cur.fetchone()   

        if not codeobjs:
            return None     

        code_hits = codeobjs[0]
        hits = (int(code_hits) + 1)
        
        cur.execute("update codes set hits = %s where id=%s",(hits,uid))
        conn.commit()            
        cur.execute("select id,title,author,tags,lang,content,hits,create_time,via\
         from codes where id = %s",uid)
        if web.config.debug:
            logger.info("execute sql: %s "%cur._executed)           
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