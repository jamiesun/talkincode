#!/usr/bin/python2.7 
#coding:utf-8
from settings import logger,pagesize
from store import get_conn

def get_tags(limit=pagesize):
    conn = get_conn()
    cur = conn.cursor()
    tagset = {}
    try:
        cur.execute("select tags  from codes")
        tags1 = cur.fetchall()
        if tags1:
            for tagrow in tags1:
                tag = tagrow[0]
                if not tag:
                    continue
                ts = tag.split(",")
                for t in ts:
                    if tagset.has_key(t):
                        tagset[t] += 1
                    else:
                        tagset[t] = 0
        cur.execute("select tags  from posts")
        tags2 = cur.fetchall()
        if tags2:
            for tagrow in tags2:
                tag = tagrow[0]
                if not tag:
                    continue
                ts = tag.split(",")
                for t in ts:
                    if tagset.has_key(t):
                        tagset[t] += 1
                    else:
                        tagset[t] = 0        
        sort_tags = sorted( tagset.items(),key=lambda d:d[1],reverse=True)
        print sort_tags
        return sort_tags[:limit]
    except Exception,e:
        logger.error("get tags error,%s"%e)
        raise e
    finally:
        cur.close()
        conn.close()   

def get_code_tags(limit=pagesize):
    conn = get_conn()
    cur = conn.cursor()
    tagset = {}
    try:
        cur.execute("select tags  from codes")
        tags1 = cur.fetchall()
        if tags1:
            for tagrow in tags1:
                tag = tagrow[0]
                if not tag:
                    continue
                ts = tag.split(",")
                for t in ts:
                    if tagset.has_key(t):
                        tagset[t] += 1
                    else:
                        tagset[t] = 0   
        sort_tags = sorted( tagset.items(),key=lambda d:d[1],reverse=True)
        return sort_tags[:limit]
    except Exception,e:
        logger.error("get post tags error,%s"%e)
        raise e
    finally:
        cur.close()
        conn.close()           

def get_post_tags(limit=pagesize):
    conn = get_conn()
    cur = conn.cursor()
    tagset = {}
    try:
        cur.execute("select tags  from posts")
        tags1 = cur.fetchall()
        if tags1:
            for tagrow in tags1:
                tag = tagrow[0]
                if not tag:
                    continue
                ts = tag.split(",")
                for t in ts:
                    if tagset.has_key(t):
                        tagset[t] += 1
                    else:
                        tagset[t] = 0   
        sort_tags = sorted( tagset.items(),key=lambda d:d[1],reverse=True)
        return sort_tags[:limit]
    except Exception,e:
        logger.error("get post tags error,%s"%e)
        raise e
    finally:
        cur.close()
        conn.close()   


if __name__ == "__main__":
    print get_code_tags()