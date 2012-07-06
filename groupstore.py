#!/usr/bin/python2.7 
#coding:utf-8
from settings import logger
from store import get_conn,todict
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




if __name__ == "__main__":
    pass