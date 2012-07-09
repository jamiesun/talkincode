#!/usr/bin/python2.7 
#coding:utf-8
from settings import logger,cache
from store import get_conn,todict
import uuid
import datetime
import web

@cache.cache('get_user_func', expire=3600)
def get_user(username):
    if not username :
        raise Exception("username not empty")
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("select id,username,nicename,email,url,authkey,created,status,lastlogin\
             from users where username=%s ",(username))
        if web.config.debug:
            logger.info("execute sql: %s "%cur._executed)        
        user = cur.fetchone()
        if not user:
            raise Exception("user not exists")
        return todict(user,cur.description)
    except Exception,e:
        logger.error("getuser error,%s"%e)
        raise e
    finally:
        cur.close()
        conn.close()    

if __name__ == "__main__":
    pass