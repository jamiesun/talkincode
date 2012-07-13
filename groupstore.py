#!/usr/bin/python2.7 
#coding:utf-8
from settings import logger,cache,pagesize
from store import get_conn,todict
import uuid
import datetime
import web
   

@cache.cache('get_user_func', expire=3600)
def get_user(uid):
    conn = get_conn()
    cur = conn.cursor()
    try:      
        cur.execute(" select id,username,email,url,authkey,lastlogin from users  WHERE id = %s",uid)
        if web.config.debug:
            logger.info("execute sql: %s "%cur._executed)        
        ones =  cur.fetchone()
        if ones :
            return todict(ones,cur.description)
        else:
            raise Exception("no result")
    except:
        raise
    finally:
        cur.close()
        conn.close()   

@cache.cache('get_user_byauthkey_func', expire=3600)
def get_user_byauthkey(authkey):
    conn = get_conn()
    cur = conn.cursor()
    try:      
        cur.execute(" select id,username,email,url,authkey,lastlogin from users  WHERE authkey = %s",authkey)
        if web.config.debug:
            logger.info("execute sql: %s "%cur._executed)        
        ones =  cur.fetchone()
        if ones :
            return todict(ones,cur.description)
        else:
            raise Exception("authkey invalid")
    except:
        raise
    finally:
        cur.close()
        conn.close()   

@cache.cache('get_post_stats_func', expire=3600)
def get_post_stats(tag):
    conn = get_conn()
    cur = conn.cursor()
    try:
        if tag:      
            cur.execute("""
                SELECT COUNT(*) AS total, SUM(hits) AS hits_total
                FROM posts 
                where tags like %s
                """,'%%%s%%'%tag)
        else:
            cur.execute("""
                SELECT COUNT(*) AS total, SUM(hits) AS hits_total
                FROM posts 
                """)            
        if web.config.debug:
            logger.info("execute sql: %s "%cur._executed)            
        ones =  cur.fetchone()
        if ones :
            return todict(ones,cur.description)
        else:
            raise Exception("no result")
    except:
        raise
    finally:
        cur.close()
        conn.close()            
      

def list_posts_by_tag(tag,page=1,limit=pagesize):
    conn = get_conn()
    cur = conn.cursor()
    offset = 0
    if page >= 1:
        offset = (page -1) * limit     
    try:      
        cur.execute("""
            SELECT p.id,p.userid,p.title,p.tags,p.description,
             p.content, p.STATUS,p.hits,p.created,p.modified,p.via
            FROM posts p
            WHERE p.tags like %s
            ORDER BY modified DESC
            LIMIT %s,%s        
            """,('%%%s%%'%tag,offset,limit))
        if web.config.debug:
            logger.info("execute sql: %s "%cur._executed)        
        result = cur.fetchall()
        return [todict(rt,cur.description) for rt in result]
    except:
        raise
    finally:
        cur.close()
        conn.close()    

def list_posts_by_user(userid,page=1,limit=pagesize):
    conn = get_conn()
    cur = conn.cursor()
    offset = 0
    if page >= 1:
        offset = (page -1) * limit     
    try:      
        cur.execute("""
            SELECT p.id,p.userid,u.username,u.email,p.title,p.tags,p.description,
             p.content, p.STATUS,p.hits,p.created,p.modified,p.via
            FROM posts p,users u
            WHERE p.userid = %s
            and p.userid = u.id
            ORDER BY modified DESC
            LIMIT %s,%s        
            """,(userid,offset,limit))
        if web.config.debug:
            logger.info("execute sql: %s "%cur._executed)        
        result = cur.fetchall()
        return [todict(rt,cur.description) for rt in result]
    except:
        raise
    finally:
        cur.close()
        conn.close()            

def list_posts_by_codeid(cid,page=1,limit=pagesize):
    conn = get_conn()
    cur = conn.cursor()
    offset = 0
    if page >= 1:
        offset = (page -1) * limit     
    try:      
        cur.execute("""
            SELECT id,userid,codeid,title,tags,description,
             content, STATUS,hits,created,modified,via
            FROM posts p
            WHERE p.codeid = %s
            ORDER BY modified DESC
            LIMIT %s,%s        
            """,(cid,offset,limit))
        if web.config.debug:
            logger.info("execute sql: %s "%cur._executed)        
        result = cur.fetchall()
        return [todict(rt,cur.description) for rt in result]
    except:
        raise
    finally:
        cur.close()
        conn.close()                  

def list_posts(page=1,limit=pagesize):
    conn = get_conn()
    cur = conn.cursor()
    offset = 0
    if page >= 1:
        offset = (page -1) * limit    
    try:
        cur.execute("""
            SELECT id,codeid,userid,title,tags,description,
            content,status,hits,created,modified,via
            FROM posts order by modified desc
            LIMIT %s,%s            
            """,(offset,limit))
        if web.config.debug:
            logger.info("execute sql: %s "%cur._executed)               
        result = cur.fetchall()
        return [todict(rt,cur.description) for rt in result]
    except Exception,e:
        logger.error('list_posts error %s'%e)
        raise
    finally:
        cur.close()
        conn.close()

def search_posts(keyword=None,page=1,limit=pagesize):
    conn = get_conn()
    cur = conn.cursor()
    offset = 0
    if page >= 1:
        offset = (page -1) * limit    
    try:
        if not keyword:
            return None
        cur.execute("""
            SELECT p.id,codeid,userid,u.username,title,tags,description,
            content,p.status,hits,p.created,modified,via
            FROM posts p,users u
            WHERE title like %s
            and p.userid = u.id
            order by hits desc
            LIMIT %s,%s            
            """,('%%%s%%'%keyword,offset,limit))
        if web.config.debug:
            logger.info("execute sql: %s "%cur._executed)               
        result = cur.fetchall()
        return [todict(rt,cur.description) for rt in result]
    except Exception,e:
        logger.error('list_posts error %s'%e)
        raise
    finally:
        cur.close()
        conn.close()        

@cache.cache('group_get_content_func', expire=3600)
def get_content(uid):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("select hits from posts where id=%s",uid)
        postobjs = cur.fetchone()   

        if not postobjs:
            return None      

        post_hits = postobjs[0]
        hits = (int(post_hits) + 1)
        
        cur.execute("update posts set hits = %s where id=%s",(hits,uid))
        conn.commit()            
        cur.execute("""
            SELECT p.id,codeid,userid,u.username,title,tags,description,
            content,p.status,hits,p.created,modified,via
            FROM posts p,users u  
            WHERE p.userid = u.id and p.id = %s    
            """,uid)     
        if web.config.debug:
            logger.info("execute sql: %s "%cur._executed)                  
        ones =  cur.fetchone()
        if ones :
            return todict(ones,cur.description)
        else:
            raise Exception("no result")
    except Exception,e:
        logger.error('get_content error %s'%e)
        raise e
    finally:
        cur.close()
        conn.close()

def add_post(userid,title=None,tags=None,content=None,codeid=None,via=None):
    logger.info("add post title=%s"%(title))
    conn = get_conn()
    cur = conn.cursor()
    try:
        if not content:
            logger.error('content can not empty')
            raise Exception('content can not empty')
        if not title: title = content[:128].replace('\n','')
        if not tags:tags = 'other'
        create_time = datetime.datetime.now().strftime( "%Y-%m-%d %H:%M:%S")
        uid = uuid.uuid4().hex
        cur.execute("""insert into posts \
            (id,codeid,title,userid,tags,content,created,modified,via)
             values(%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
             (uid,codeid,title,userid,tags,content,create_time,create_time,via))
        if web.config.debug:
            logger.info("execute sql: %s "%cur._executed)        
        conn.commit()
    except Exception,e:
        conn.rollback()
        logger.error("add_post error %s"%e)
        raise e
    finally:
        cur.close()
        conn.close()    

def update_post(uid,userid,title=None,content=None,tags=None):
    logger.info("update post id=%s"%(uid))
    if not uid:return
    if not content:
        logger.error('content can not empty')
        raise Exception('content can not empty') 
    conn = get_conn()
    cur = conn.cursor()
    try:
        modified = datetime.datetime.now().strftime( "%Y-%m-%d %H:%M:%S")
        cur.execute("select id,title,content,tags from posts where id=%s and userid=%s",(uid,userid))
        postobj = cur.fetchone()
        if not postobj:
            raise Exception("post not exists or you are not the author ")

        if not title:title = postobj['title']
        if not tags:tags = postobj['tags']

        cur.execute("update posts set title=%s,content=%s,tags=%s,modified = %s  where id = %s",
            (title,content,tags,modified,uid))
        if web.config.debug:
            logger.info("execute sql: %s "%cur._executed)        
        conn.commit()
    except Exception,e:
        conn.rollback()
        logger.error("update_post error %s"%e)
        raise e
    finally:
        cur.close()
        conn.close() 

def update_post_tags(uid,tags=None):
    logger.info("update post id=%s"%(uid))
    if not uid:return
    if not tags:tags = "other"
    conn = get_conn()
    cur = conn.cursor()
    try:
        modified = datetime.datetime.now().strftime( "%Y-%m-%d %H:%M:%S")
        cur.execute("update posts set tags= %s modified = %s where id = %s",(tags,modified,uid))
        if web.config.debug:
            logger.info("execute sql: %s "%cur._executed)        
        conn.commit()
    except Exception,e:
        conn.rollback()
        logger.error("update_post error %s"%e)
        raise e
    finally:
        cur.close()
        conn.close()             

def del_content(uid):
    conn = get_conn()
    cur = conn.cursor()
    if not uid:
        return
    try:
        cur.execute("delete from posts where id=%s",(uid))
        if web.config.debug:
            logger.info("execute sql: %s "%cur._executed)        
        conn.commit()            
    except:
        raise
    finally:
        cur.close()
        conn.close()

def add_comment(postid,content,userid=None,author=None,email=None,url=None,ip=None,agent=None,status=0,via=None):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("select count(*) from posts where id = %s",postid)
        if cur.fetchone()[0] == 0:
            raise Exception("post not exists")
        modified = datetime.datetime.now().strftime( "%Y-%m-%d %H:%M:%S")
        uid = uuid.uuid4().hex
        cur.execute("""
        INSERT INTO comments
        (id, postid, author,content, userid, email, url, ip, agent,status, created,via)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s) """,
        (uid,postid,author,content,userid,email,url,ip,agent,status,modified,via))
        if web.config.debug:
            logger.info("execute sql: %s "%cur._executed)        
        conn.commit()            
    except Exception,e:
        logger.error("add_comment error %s"%e)
        raise
    finally:
        cur.close()
        conn.close()

def list_comments(pid,page=1,limit=pagesize):
    conn = get_conn()
    cur = conn.cursor()
    offset = 0
    if page >= 1:
        offset = (page -1) * limit    
    try:
        cur.execute("""
            SELECT id,postid,author,content,userid,url,created,via
            FROM comments
            WHERE postid = %s order by created asc
            LIMIT %s,%s            
            """,(pid,offset,limit))
        if web.config.debug:
            logger.info("execute sql: %s "%cur._executed)        
        result = cur.fetchall()
        return [todict(rt,cur.description) for rt in result]
    except Exception,e:
        logger.error('list_comments error %s'%e)
        raise
    finally:
        cur.close()
        conn.close()        

if __name__ == "__main__":
    print list_posts_by_guid("python")