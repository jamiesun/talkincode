#!/usr/bin/python2.7 
#coding:utf-8
"""
@description:mysql of python 
"""
import MySQLdb
from settings import logger,cache
from DBUtils.PooledDB import PooledDB
import uuid
import datetime
import web
from sqlbean.db import connection

dbpool = PooledDB(creator=MySQLdb,
maxusage=1000,
host='localhost',
user='root',
passwd='root',
db='talkincode_db1',
charset="utf8")

get_conn = lambda : dbpool.connection()

DATABASE = dbpool.connection()
DATABASE.b_commit = True

def get_db_by_table(table_name):
    return DATABASE
connection.get_db_by_table = get_db_by_table

from sqlbean.shortcut import Model
from sqlbean.db.query import Query


class User(Model):

    def __getitem__(self,key):
        return getattr(self,key)    

    class Meta:
        pk = "id"
        table="users"
        
class Post(Model):
    
    def __getitem__(self,key):
        return getattr(self,key)    

    class Meta:
        pk = "id"
        table="posts"

class Code(Model):
    
    def __getitem__(self,key):
        return getattr(self,key)    

    class Meta:
        pk = "id"
        table="codes"

class Project(Model):
    
    def __getitem__(self,key):
        return getattr(self,key)    

    class Meta:
        pk = "id"  
        table="projects"      

class Comment(Model):

    def __getitem__(self,key):
        return getattr(self,key)    
         
    class Meta:
        pk = "id"  
        table="comments"  

class Tag(Model):
    
    def __getitem__(self,key):
        return getattr(self,key)    

    class Meta:
        pk = "id"  
        table="tags"    

class Lang(Model):
    
    def __getitem__(self,key):
        return getattr(self,key)    

    class Meta:
        pk = "id" 
        table = "langs"         

class Authkey(Model):
    
    def __getitem__(self,key):
        return getattr(self,key)    
             
    class Meta:
        pk = "authkey" 
        table = "authkeys"         


post_page  = lambda: Query(model=Post)    
code_page  = lambda: Query(model=Code)           

def todict(row,rowdesc):
    d = {}
    for idx, col in enumerate(rowdesc):
        d[col[0]] = row[idx]
    return d

def nextid():
    return uuid.uuid4().hex

def currtime():
    return datetime.datetime.now().strftime( "%Y-%m-%d %H:%M:%S")

def register(username,password,email):
    if not username or not password or not email:
        raise Exception("username,password,email not empty")
    try:
        if User.count(username=username):
            raise Exception("username already exists")

        if User.count(email=email):
            raise Exception("email already exists")    

        authkey = Authkey()
        authkey.authkey = uuid.uuid4().hex
        authkey.consumer = username
        authkey.description = ""
        authkey.hits = 0
        authkey.status = 1
        authkey.create_time = datetime.datetime.now().strftime( "%Y-%m-%d %H:%M:%S")

        user  = User()
        user.id = authkey.authkey
        user.username = username
        user.nicename = username
        user.email = email
        user.password = password
        user.authkey = authkey.authkey
        user.created = authkey.create_time
        user.lastlogin = authkey.create_time

        User.begin()
        authkey.save()
        user.save()
        User.commit()


        return user
    except Exception,e:
        User.rollback()
        logger.error("register error,%s"%e)
        raise e

def login(username,password):
    if not username or not password :
        raise Exception("username,password not empty")

    try:
        user = User.get(username=username,password=password)
        if not user:
            raise Exception("user not exists")

        user.lastlogin = datetime.datetime.now().strftime( "%Y-%m-%d %H:%M:%S")
        user.save()
        return user

    except Exception,e:
        logger.error("login error,%s"%e)
        raise e

def sitemap_data():
    urlset = []
    try:
        for post in Post.where(status=1):
            lastmod_tmp = datetime.datetime.strptime(post.modified,"%Y-%m-%d %H:%M:%S")
            lastmod = lastmod_tmp.strftime("%Y-%m-%dT%H:%M:%SZ")
            url = dict(loc="http://www.talkincode.org/news/post/view/%s"%post.id,
                       lastmod=lastmod,chgfreq="daily")
            urlset.append(url)


        for code in Code.where():
            lastmod_tmp = datetime.datetime.strptime(code.create_time,"%Y-%m-%d %H:%M:%S")
            lastmod = lastmod_tmp.strftime("%Y-%m-%dT%H:%M:%SZ")
            url = dict(loc="http://www.talkincode.org/code/view/%s"%code.id,
                       lastmod=lastmod,chgfreq="monthly")
            urlset.append(url)       

        for proj in Project.where():
            lastmod_tmp = datetime.datetime.strptime(proj.created,"%Y-%m-%d %H:%M:%S")
            lastmod = lastmod_tmp.strftime("%Y-%m-%dT%H:%M:%SZ")
            url = dict(loc="http://www.talkincode.org/open/proj/view/%s"%proj.id,
                       lastmod=lastmod,chgfreq="monthly")
            urlset.append(url)                             
          
        return urlset
    except Exception,e:
        logger.error("login error,%s"%e)
        return []

def get_tags(limit):
    tagset = {}
    try:
        for code in Code.where():
            tag = code.tags
            if not tag:
                continue
            ts = tag.split(",")
            for t in ts:
                if tagset.has_key(t):
                    tagset[t] += 1
                else:
                    tagset[t] = 1

        for post in Post.where(status=1):
            tag = post.tags
            if not tag:
                continue
            ts = tag.split(",")
            for t in ts:
                if tagset.has_key(t):
                    tagset[t] += 1
                else:
                    tagset[t] = 1       
        sort_tags = sorted( tagset.items(),key=lambda d:d[1],reverse=True)
        print sort_tags
        return sort_tags[:limit]
    except Exception,e:
        logger.error("get tags error,%s"%e)
        raise e

#@cache.cache('get_code_tags_func', expire=3600)
def get_code_tags(limit):
    tagset = {}
    try:
        for code in Code.where():
            tag = code.tags
            if not tag:
                continue
            ts = tag.split(",")
            for t in ts:
                if tagset.has_key(t):
                    tagset[t] += 1
                else:
                    tagset[t] = 1  
        sort_tags = sorted( tagset.items(),key=lambda d:d[1],reverse=True)
        return sort_tags[:limit]
    except Exception,e:
        logger.error("get post tags error,%s"%e)
        raise e

def get_post_tags(limit):
    tagset = {}
    try:
        for post in Post.where(status=1):
            tag = post.tags
            if not tag:
                continue
            ts = tag.split(",")
            for t in ts:
                if tagset.has_key(t):
                    tagset[t] += 1
                else:
                    tagset[t] = 1  
        sort_tags = sorted( tagset.items(),key=lambda d:d[1],reverse=True)
        return sort_tags[:limit]
    except Exception,e:
        logger.error("get post tags error,%s"%e)
        raise e

def get_project_tags(limit):
    tagset = {}
    try:
        for proj in Project.where():
            tag = proj.tags
            if not tag:
                continue
            ts = tag.split(",")
            for t in ts:
                if tagset.has_key(t):
                    tagset[t] += 1
                else:
                    tagset[t] = 1   
        sort_tags = sorted( tagset.items(),key=lambda d:d[1],reverse=True)
        return sort_tags[:limit]
    except Exception,e:
        logger.error("get post tags error,%s"%e)
        raise e

#@cache.cache('get_post_stats_func', expire=3600)
def get_post_stats(tag):
    try:
        if tag:      
            cur = Post.raw_sql("""
                SELECT COUNT(*) AS total, SUM(hits) AS hits_total
                FROM posts 
                where tags like %s
                """,'%%%s%%'%tag)
        else:
            cur = Post.raw_sql("""
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

@cache.cache('get_user_func', expire=3600)
def get_user(id):
    return User.get(id)

# def initdata():
#     conn = get_conn()
#     cur = conn.cursor()
#     grps = {"python":"python编程",
#             "php":"php编程",
#             "html":"html&css",
#             "func":"函数式编程",
#             "st2":"sublime text 2小站",
#             "vim":"vim小站",
#             "emacs":"emacs小站"}
#     langs = {"c":"c",
#              "c++":"cpp",
#              "java":"java",
#              "c#":"cs",
#              "python":"py",
#              "ruby":"rb",
#              "php":"php",
#              "perl":"pl",
#              "objective-c":"c",
#              "vb":"vb",
#              "javascript":"js",
#              "pascal":"pas",
#              "lisp":"lsp",
#              "sql":"sql",
#              "lua":"lua",
#              "matlab":"m",
#              "shell":"sh",
#              "golang":"go"}
#     try:
#         count = 0
#         cur.execute("delete from langs")
#         for k,l in langs.items():
#             count += 1 
#             cur.execute("insert into langs (id,name,ext,hits) values(%s,%s,%s,%s)",(count,k,l,0))
#         cur.execute("delete from groups")
#         count = 0
#         for k,g in grps.items():
#             count += 1 
#             cur.execute("insert into groups (id,name,guid,posts) values(%s,%s,%s,%s)",(count,g,k,0))     
#         cur.execute("insert into groups (id,name,guid,posts) values(%s,%s,%s,%s)",(0,"综合讨论","all",0))    
#         conn.commit()
#     except Exception, e:
#         raise e
#     finally:
#         cur.close()
#         conn.close()    


if __name__ == "__main__":
    """pass"""
    p0 = post_page().where()[0:20]
    p1 = Post.where()[15:300]
    print len(p0)
    print len(p1)



