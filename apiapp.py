#!/usr/bin/python2.7 
#coding:utf-8
from settings import route_app,logger
import store 
import json
import web
import traceback
from sqlbean.shortcut import Model
from re import escape
"""
@description:talkincode.org  api
"""
app  = route_app()

def fromModel(obj):
    if isinstance(obj,Model):
        dd = {}
        for fd in obj._fields:
            val = getattr(obj,fd)
            if isinstance(val,unicode):
                dd[fd] = val.encode("utf-8")
            else:
                dd[fd] = val 
        return dd
    return obj

def jsonResult(**kwargs):
    return json.dumps(kwargs,default=fromModel)

def doauthkey(func):
    def func_warp(*args,**argkv):
        authkey = web.input().get("authkey")
        if not authkey:
            return jsonResult(error="authkey can not empty") 
        if type(authkey) == unicode:
            authkey = str(authkey)            

        try:
            authkey = store.Authkey.get(authkey=authkey)
            if not authkey:
                return jsonResult(error="authkey not exists") 

            authkey.hits += 1
            authkey.save()
            store.Authkey.commit()
            return func(*args,**argkv)
        except:
            raise
    return func_warp        

@app.route("/register")
class register():
    def POST(self):
        form = web.input()
        username = form.get("username")
        password = form.get("password")
        email = form.get("email")
        if not username or not password:
            return jsonResult(error=u"username,password can't empty") 
        if not email:
            return jsonResult(error=u"email can't empty")
        try:
            user = store.register(username,password,email)
            return jsonResult(username=username,email=email,authkey=user["authkey"])
        except Exception,e:
            traceback.print_exc()
            return jsonResult(error="register error %s"%e)

@app.route("/code/add")
class code_add():
    @doauthkey
    def POST(self):
        forms = web.input()
        code = store.Code(id=store.nextid(),
                      parent=forms.get("pid"),
                      title = forms.get("title"),
                      author = forms.get("author"),
                      email = forms.get("email"),
                      tags = forms.get("tags"),
                      content = forms.get("content"),
                      authkey = forms.get("authkey"),
                      filename = forms.get("filename"),
                      lang=forms.get("lang"),
                      via=forms.get("via"),
                      create_time=store.currtime())
        try:
            code.save()
            store.Code.commit()
            return jsonResult(result="code publish success")
        except:
            return jsonResult(error="code publish fail")

@app.route("/code/index")
class code_index():
    def GET(self):
        web.header("Content-Type","text/html; charset=utf-8")
        keyword = web.input().get("q") 
        limit = int(web.input().get("limit",1000))
        if limit > 1000:limit = 1000  
        try:
            tops = store.Code.where("title like %s",'%%%s%%'%keyword)\
                         .order_by("-create_time")[:limit]
            return json.dumps(list(tops),default=fromModel)
        except Exception,e:
            traceback.print_exc()
            logger.error("query data error %s"%e)
            return jsonResult(error="query data error ")         

@app.route("/code/my")
class code_index_my():
    @doauthkey
    def GET(self):
        web.header("Content-Type","text/html; charset=utf-8")
        authkey = web.input().get("authkey") 
        limit = int(web.input().get("limit",1000))
        if limit > 1000:limit = 1000  
        try:
            tops = store.Code.where(authkey=authkey).order_by("-create_time")[:limit]
            return json.dumps(list(tops),default=fromModel)
        except Exception,e:
            logger.error("query data error %s"%e)
            return jsonResult(error="query data error ")                 

@app.route("/code/get/(.*)")
class code_get():
    def GET(self,uid):
        web.header("Content-Type","text/html; charset=utf-8")
        try:
            content = store.Code.get(uid)
            return json.dumps(content,default=fromModel)
        except:
            return jsonResult(error="query data error")  
  

@app.route("/post/add")
class add_post():
    @doauthkey
    def POST(self):
        post = store.Post(id=store.nextid())
        form = web.input()
        post.authkey = form.get("authkey")
        user = store.User.get(authkey=post.authkey)
        post.userid = user.id
        post.codeid = form.get("codeid")
        post.title = form.get("title")
        post.tags = form.get("tags")
        post.content = form.get("content")
        post.via = form.get("via")
        post.created = post.modified = store.currtime()
        if not post.title or not post.content:
            return jsonResult(error="title,content can not empty")
        try:
            post.save()
            store.Post.commit()
            return jsonResult(result="post success")
        except Exception, e:
            return jsonResult(error="post fail %s"%e)

@app.route("/post/update")
class update_post():
    @doauthkey
    def POST(self):
        form = web.input()
        authkey = form.get("authkey")
        user = store.User.get(authkey=authkey)
        userid = user.get("id")        
        postid = form.get("postid")
        post = store.Post.get(postid=postid,userid=userid)
        if not post :
            return jsonResult(error="you are not the post author")

        post.title = form.get("title")
        post.tags = form.get("tags",'other')
        post.content = form.get("content")
        post.modified = store.currtime()
        if not post.postid  or not post.content:
            return jsonResult(error="postid,content can not empty")
        try:
            post.save()
            store.Post.commit()
            return jsonResult(result="update post success")
        except Exception, e:
            return jsonResult(error="update post fail %s"%e)            

@app.route("/comment/add")
class add_comment():
    @doauthkey
    def POST(self):
        try:
            comment = store.Comment(id=store.nextid())
            form = web.input()
            authkey = form.get("authkey")
            user = store.User.get(authkey=authkey)
            comment.userid = user.id
            comment.author = user.username
            comment.content = form.get("content")
            comment.postid = form.get("postid")
            comment.via=form.get("via")
            comment.email = user.email
            comment.url = user.url
            comment.ip = web.ctx.ip
            comment.agent =  web.ctx.env.get('HTTP_USER_AGENT')
            comment.status = 1
            if not comment.content:
                return jsonResult(error="content can not empty")
            comment.save()
            store.Comment.commit()
            return jsonResult(result="post comment success")
        except Exception, e:
            return jsonResult(error="add comment error %s"%e)    


@app.route("/post/index")
class post_index():
    def GET(self):
        web.header("Content-Type","text/html; charset=utf-8")
        keyword = web.input().get("q",'') 
        limit = int(web.input().get("limit",100))   
        if limit > 1000:limit = 1000     
        try:
            sql = """
            SELECT p.id,codeid,userid,u.username,title,tags,description,
            content,p.status,hits,p.created,modified,via
            FROM posts p,users u
            WHERE title like '%s'
            and p.userid = u.id
            order by hits desc
            LIMIT %s,%s            
            """%('%%%s%%'%escape(keyword),0,limit)

            cur =  store.Post.raw_sql(sql)
            result = cur.fetchall()
            return json.dumps([store.todict(rt,cur.description) for rt in result])
        except Exception,e:
            return jsonResult(error="query post fail %s"%e)

@app.route("/post/my")
class post_index():
    def GET(self):
        web.header("Content-Type","text/html; charset=utf-8")
        authkey = web.input().get("authkey") 
        user = store.User.get(authkey=authkey)
        userid = user.id
        limit = int(web.input().get("limit",100))   
        if limit > 1000:limit = 1000     
        try:
            cur =store.Post.raw_sql("""
            SELECT p.id,p.userid,u.username,u.email,p.title,p.tags,p.description,
             p.content, p.STATUS,p.hits,p.created,p.modified,p.via
            FROM posts p,users u
            WHERE p.userid = '%s'
            and p.userid = u.id
            ORDER BY modified DESC
            LIMIT %s,%s      
            """%(escape(userid),0,limit))
            result = cur.fetchall()
            return json.dumps([store.todict(rt,cur.description) for rt in result])
        except Exception,e:
            return jsonResult(error="query post fail %s"%e)            

@app.route("/post/get/(.*)")
class get_post():
    def GET(self,uid):
        web.header("Content-Type","text/html; charset=utf-8")
        try:
            pcur = store.Post.raw_sql("""SELECT p.id,codeid,userid,u.username,title,tags,description,
            content,p.status,hits,p.created,modified,via
            FROM posts p,users u  
            WHERE p.userid = u.id and p.id = '%s'  
            """%escape(uid))
            post = store.todict(pcur.fetchone(),pcur.description)
            comments = store.Comment.where(postid=post.get("id")).order_by("-created")
            result = jsonResult(post=post,comments=list(comments))
            return result
        except Exception,e:
            import traceback
            traceback.print_exc()
            return jsonResult(error="error %s"%e)


if  __name__ == "__main__":
    print jsonResult(name="sd",sfd="sdf")