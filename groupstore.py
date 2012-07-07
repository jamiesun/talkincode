#!/usr/bin/python2.7 
#coding:utf-8
from settings import logger,cache
from store import get_conn,todict
import uuid
import datetime

@cache.cache('get_group_func', expire=3600)
def get_group(gid):
    conn = get_conn()
    cur = conn.cursor()
    try:      
        cur.execute(" select id,name,description,guid,posts from groups  WHERE id = %s",gid)
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

@cache.cache('get_user_func', expire=3600)
def get_user(uid):
    conn = get_conn()
    cur = conn.cursor()
    try:      
        cur.execute(" select id,username,email,url,authkey,lastlogin from users  WHERE id = %s",uid)
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

@cache.cache('get_post_total_func', expire=3600)
def get_post_stats(guid=None):
    conn = get_conn()
    cur = conn.cursor()
    try:      
        if guid:
            cur.execute("""
                SELECT COUNT(*) AS total, SUM(hits) AS hits_total
                FROM posts p,groups g
                WHERE p.groupid = g.id AND g.guid = %s
                """,guid)
        else:
            cur.execute(" select count(*) as total, sum(hits) as hits_total from posts ")
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

def list_groups():
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("select id,name,description,guid,posts from groups order by posts desc")
        result = cur.fetchall()
        return [todict(rt,cur.description) for rt in result]
    except Exception,e:
        logger.error('list_groups error %s'%e)
        raise
    finally:
        cur.close()
        conn.close()

#@cache.cache('list_posts_by_guid_func', expire=3600)
def list_posts_by_guid(guid,page=1,limit=30):
    conn = get_conn()
    cur = conn.cursor()
    cpage = page
    if page >= 1:
        cpage = page-1    
    try:      
        cur.execute("""
            SELECT p.id,p.groupid,p.userid,p.title,p.tags,p.description,
             p.content, p.STATUS,p.hits,p.created,p.modified
            FROM posts p,groups g
            WHERE p.groupid = g.id AND g.guid = %s
            ORDER BY modified DESC
            LIMIT %s,%s        
            """,(guid,cpage,limit))
        result = cur.fetchall()
        return [todict(rt,cur.description) for rt in result]
    except:
        raise
    finally:
        cur.close()
        conn.close()            

def list_posts(gid=None,page=1,limit=30):
    conn = get_conn()
    cur = conn.cursor()
    cpage = page
    if page >= 1:
        cpage = page-1
    try:
        if gid:
            cur.execute("""
                SELECT id,groupid,userid,title,tags,description,
                content,status,hits,created,modified
                FROM posts  
                WHERE groupid = %s order by modified desc
                LIMIT %s,%s            
                """,(gid,cpage,limit))
        else:
             cur.execute("""
                SELECT id,groupid,userid,title,tags,description,
                content,status,hits,created,modified
                FROM posts order by modified desc
                LIMIT %s,%s            
                """,(cpage,limit))
        result = cur.fetchall()
        return [todict(rt,cur.description) for rt in result]
    except Exception,e:
        logger.error('list_posts error %s'%e)
        raise
    finally:
        cur.close()
        conn.close()


def get_content(uid):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("select hits from posts where id=%s",uid)
        postobjs = cur.fetchone()   

        if not postobjs:
            raise Exception('post not exists')         

        post_hits = postobjs[0]
        hits = (int(post_hits) + 1)
        
        cur.execute("update posts set hits = %s where id=%s",(hits,uid))
        conn.commit()            
        cur.execute("""
            SELECT id,groupid,userid,title,tags,description,
            content,status,hits,created,modified
            FROM posts  
            WHERE id = %s    
            """,uid)
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

def add_post(gid,userid,title=None,tags=None,content=None):
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
            (id,groupid,title,userid,tags,content,created,modified)
             values(%s,%s,%s,%s,%s,%s,%s,%s)""",
             (uid,gid,title,userid,tags,content,create_time,create_time))
        conn.commit()
    except Exception,e:
        conn.rollback()
        logger.error("add_post error %s"%e)
        raise e
    finally:
        cur.close()
        conn.close()    

def update_post(uid,content=None):
    logger.info("update post id=%s"%(uid))
    if not uid:return
    if not content:
        logger.error('content can not empty')
        raise Exception('content can not empty') 
    conn = get_conn()
    cur = conn.cursor()
    try:
        modified = datetime.datetime.now().strftime( "%Y-%m-%d %H:%M:%S")
        cur.execute("update posts set content= %s modified = %s  where id = %s",(content,modified,uid))
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
        conn.commit()            
    except:
        raise
    finally:
        cur.close()
        conn.close()

def add_comment(postid,content,userid=None,author=None,email=None,url=None,ip=None,agent=None,status=0):
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
        (id, postid, author,content, userid, email, url, ip, agent,status, created)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s) """,
        (uid,postid,author,content,userid,email,url,ip,agent,status,modified))
        conn.commit()            
    except Exception,e:
        logger.error("add_comment error %s"%e)
        raise
    finally:
        cur.close()
        conn.close()

def list_comments(pid,page=1,limit=30):
    conn = get_conn()
    cur = conn.cursor()
    cpage = page
    if page >= 1:
        cpage = page-1
    try:
        cur.execute("""
            SELECT id,postid,author,content,userid,url,created
            FROM comments
            WHERE postid = %s order by created desc
            LIMIT %s,%s            
            """,(pid,cpage,limit))
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