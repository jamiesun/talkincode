#!/usr/bin/python2.7 
#coding:utf-8
from settings import logger
from store import get_conn,todict,doauthkey,PUBLIC_KEY
import uuid
import datetime



def list_groups():
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("select id,name,guid,posts from groups order by posts desc")
        result = cur.fetchall()
        return [todict(rt,cur.description) for rt in result]
    except Exception,e:
        logger.error('list_groups error %s'%e)
        raise
    finally:
        cur.close()
        conn.close()



@doauthkey
def add_post(title=None,descrition=None,tags=None,content=None,authkey=None):
    if authkey == PUBLIC_KEY:
        raise Exception("not accept public authkey")
    logger.info("add post title=%s"%(title))
    conn = get_conn()
    cur = conn.cursor()
    try:
        if not content:
            logger.error('content can not empty')
            raise Exception('content can not empty')

        if not title: title = content[:128].replace('\n','')
        if not email:email = '@'
        if not tags:tags = 'other'
        create_time = datetime.datetime.now().strftime( "%Y-%m-%d %H:%M:%S")
        uid = uuid.uuid4().hex
        cur.execute("insert into posts \
            (id,title,authkey,description,tags,content,created,modified)\
             values(%s,%s,%s,%s,%s,%s,%s,%s)",
             (uid,title,authkey,description,tags,content,create_time,create_time))
        conn.commit()
    except Exception,e:
        conn.rollback()
        logger.error("add_post error %s"%e)
        raise e
    finally:
        cur.close()
        conn.close()    



if __name__ == "__main__":
    pass