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


PUBLIC_KEY = '494ec9f9cbaf40cfa8d4b44447374d27'

def doauthkey(func):
    def func_warp(*args,**argkv):
        authkey = argkv.get("authkey")
        if not authkey:
            authkey=PUBLIC_KEY
        if type(authkey) == unicode:
            authkey = str(authkey)            
        conn = get_conn()
        cur = conn.cursor()
        try:
            cur.execute("select authkey,hits from authkeys where authkey=%s",(authkey))
            keyobjs = cur.fetchone()
            if not keyobjs:
                raise Exception('authkey not exists')
            authkey_hits = keyobjs[0][1]
            hits = int(authkey_hits) + 1
            cur.execute("update authkeys set hits = %s where authkey=%s",(hits,authkey))
            conn.commit()
            return func(*args,**argkv)
        finally:
            cur.close()
            conn.close()
    return func_warp        


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
        return dict(username=username,email=email,authkey=authkey,lastlogin=create_time)
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
        cur.execute("select username,email,url,authkey,lastlogin\
             from users where username=%s and password= %s",(username,password))
        user = cur.fetchone()
        if not user:
            raise Exception("user not exists")
        return dict(username=user[0],email=user[1],url=user[2],authkey=user[3],lastlogin=user[4])
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
    langs = "c,c++,java,c#,python,ruby,php,perl,objective-c,vb,javascript, pascal,Lisp,sql,ada,lua,matlab,shell,go"
    langarray = langs.split(",")
    try:
        cur.execute("delete from langs")
        for la in langarray:
            cur.execute("insert into langs (name,hits) values(%s,%s)",(la,0))
        cur.execute("delete from groups")
        for k,g in grps.items():
            cur.execute("insert into groups (name,guid,posts) values(%s,%s,%s)",(g,k,0))        
        conn.commit()
    except Exception, e:
        raise e
    finally:
        cur.close()
        conn.close()    


if __name__ == "__main__":
    #initdata()
    register("test2","123456","test@com")


