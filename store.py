#!/usr/bin/python2.7 
#coding:utf-8
"""
@description:mysql of python 
"""
import MySQLdb
from settings import logger
from DBUtils.PooledDB import PooledDB
import uuid
import datetime

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


def register(username,password,email):
    if not username or not password or not email:
        raise Exception("username,password,email not empty")
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("select count(*) from users where username=%s",username)
        user_exists = cur.fetchone()[0]
        if user_exists:
            raise Exception("user already exists")

        authkey = uuid.uuid4().hex
        create_time = datetime.datetime.now().strftime( "%Y-%m-%d %H:%M:%S")
        cur.execute("insert into authkeys values(%s,%s,%s,%s,%s,%s)",(authkey,username,"",0,create_time,1))
        cur.execute("insert into users (id,username,nicename,password,email,authkey,created,lastlogin)\
                      values (%s,%s,%s,%s,%s,%s,%s,%s)",\
                    (authkey,username,username,password,email,authkey,create_time,create_time))
        conn.commit()
        return dict(id=authkey,username=username,email=email,authkey=authkey,lastlogin=create_time)
    except Exception,e:
        logger.error("register error,%s"%e)
        raise e
    finally:
        cur.close()
        conn.close()

def login(username,password):
    if not username or not password :
        raise Exception("username,password not empty")
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("select id,username,email,url,authkey,lastlogin\
             from users where username=%s and password= %s",(username,password))
        user = cur.fetchone()

        if not user:
            raise Exception("user not exists")
        lastlogin = datetime.datetime.now().strftime( "%Y-%m-%d %H:%M:%S")
        cur.execute("update users set lastlogin = %s where id= %s",(lastlogin,user[0]))
        conn.commit()
        return dict(id=user[0],username=user[1],email=user[2],url=user[3],authkey=user[4],lastlogin=user[5])
    except Exception,e:
        logger.error("register error,%s"%e)
        raise e
    finally:
        cur.close()
        conn.close()     


def initdata():
    conn = get_conn()
    cur = conn.cursor()
    grps = {"python":"python编程",
            "php":"php编程",
            "html":"html&css",
            "st2":"sublime text 2小站",
            "vim":"vim小站",
            "emacs":"emacs小站"}
    langs = {"c":"c",
             "c++":"cpp",
             "java":"java",
             "c#":"cs",
             "python":"py",
             "ruby":"rb",
             "php":"php",
             "perl":"pl",
             "objective-c":"c",
             "vb":"vb",
             "javascript":"js",
             "pascal":"pas",
             "lisp":"lsp",
             "sql":"sql",
             "lua":"lua",
             "matlab":"m",
             "shell":"sh",
             "golang":"go"}
    try:
        count = 0
        cur.execute("delete from langs")
        for k,l in langs.items():
            count += 1 
            cur.execute("insert into langs (id,name,ext,hits) values(%s,%s,%s,%s)",(count,k,l,0))
        cur.execute("delete from groups")
        count = 1
        for k,g in grps.items():
            count += 1 
            cur.execute("insert into groups (id,name,guid,posts) values(%s,%s,%s,%s)",(count,g,k,0))     
        cur.execute("insert into groups (id,name,guid,posts) values(%s,%s,%s,%s)",(0,"综合讨论","all",0))    
        conn.commit()
    except Exception, e:
        raise e
    finally:
        cur.close()
        conn.close()    


if __name__ == "__main__":
    # initdata()
    #register("test2","123456","test@com")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("select count(*) from posts where id=%s","1")
    print (cur._executed)
    cur.close()
    conn.close()


