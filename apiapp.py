#!/usr/bin/python2.7 
#coding:utf-8
from settings import route_app,logger
import codestore
import groupstore
import store 
import json
import web
import traceback
"""
@description:talkincode.org  api
"""
app  = route_app()

def jsonResult(**kwargs):
    return json.dumps(kwargs)

def doauthkey(func):
    def func_warp(*args,**argkv):
        authkey = web.input().get("authkey")
        if not authkey:
            return jsonResult(error="authkey can not empty") 
        if type(authkey) == unicode:
            authkey = str(authkey)            
        conn = store.get_conn()
        cur = conn.cursor()
        try:
            cur.execute("select authkey,hits from authkeys where authkey=%s",(authkey))
            keyobjs = cur.fetchone()
            if not keyobjs:
                return jsonResult(error="authkey not exists") 
            authkey_hits = keyobjs[1]
            hits = int(authkey_hits) + 1
            cur.execute("update authkeys set hits = %s where authkey=%s",(hits,authkey))
            conn.commit()
            return func(*args,**argkv)
        finally:
            cur.close()
            conn.close()
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
            usession = web.ctx.session
            usession["user"] = user 
            return jsonResult(username=username,email=email,authkey=user["authkey"])
        except Exception,e:
            traceback.print_exc()
            return jsonResult(error="register error %s"%e)

@app.route("/code/add")
class code_add():
    @doauthkey
    def POST(self):
        forms = web.input()
        params = dict(pid=forms.get("pid"),
                      title = forms.get("title"),
                      author = forms.get("author"),
                      email = forms.get("email"),
                      tags = forms.get("tagstr"),
                      content = forms.get("content"),
                      authkey = forms.get("authkey"),
                      filename = forms.get("filename"),
                      lang=forms.get("lang"),
                      via=forms.get("via"))
        try:
            codestore.add_code(**params)
            return jsonResult(result="code publish success")
        except:
            return jsonResult(error="code publish fail")

@app.route("/code/index")
class code_index():
    def GET(self):
        keyword = web.input().get("q") 
        limit = int(web.input().get("limit",1000))
        try:
            tops = codestore.list_index(keyword=keyword,limit=limit) 
            return json.dumps(tops)
        except Exception,e:
            logger.error("query data error %s"%e)
            return jsonResult(error="query data error ")         

@app.route("/code/get/(.*)")
class code_get():
    def GET(self,uid):
        try:
            content = codestore.get_content(uid)
            return json.dumps(content)
        except:
            return jsonResult(error="query data error")  

@app.route("/groups")
class groups():
    def GET(self):
        try:
            grps = groupstore.list_groups()
            return json.dumps(grps)
        except:
            return jsonResult(error="query data error")         


@app.route("/post/add")
class add_post():
    @doauthkey
    def POST(self):
        form = web.input()
        authkey = form.get("authkey")
        user = groupstore.get_user_byauthkey(authkey)
        userid = user.get("id")
        codeid = form.get("codeid")
        title = form.get("title")
        tags = form.get("tags")
        gid = form.get("gid",0)
        content = form.get("content")
        via = form.get("via")
        if not title or not content:
            return jsonResult(error="title,content can not empty")
        try:
            if tags :tags = tags[:255]
            title = title[:255]
            groupstore.add_post(gid,userid,title,tags,content,codeid,via)
            return jsonResult(result="post success")
        except Exception, e:
            return jsonResult(error="post fail %s"%e)

@app.route("/comment/add")
class add_comment():
    @doauthkey
    def POST(self):
        try:
            form = web.input()
            authkey = form.get("authkey")
            user = groupstore.get_user_byauthkey(authkey)
            userid = user.get("id")
            content = form.get("content")
            postid = form.get("postid")
            via=form.get("via")
            author =  user["username"]
            email = user['email']
            url = user['url']
            ip = web.ctx.ip
            agent =  web.ctx.env.get('HTTP_USER_AGENT')
            status = 1
            if not content:
                return jsonResult(error="content can not empty")
            groupstore.add_comment(postid,content,userid,author,email,url,ip,agent,status,via)
            return jsonResult(result="post comment success")
        except Exception, e:
            return jsonResult(error="add comment error %s"%e)    


@app.route("/post/index")
class post_index():
    def GET(self):
        keyword = web.input().get("q") 
        limit = int(web.input().get("limit",100))   
        if limit > 1000:limit = 1000     
        try:
            tops = groupstore.search_posts(keyword,limit=limit) 
            return json.dumps(tops)
        except Exception,e:
            return jsonResult(error="query post fail %s"%e)

@app.route("/post/get/(.*)")
class get_post():
    def GET(self,uid):
        try:
            post = groupstore.get_content(uid)
            comments = groupstore.list_comments(uid,limit=100)
            return jsonResult(post=post,comments=comments)
        except Exception,e:
            return jsonResult(error="error %s"%e)


if  __name__ == "__main__":
    print jsonResult(name="sd",sfd="sdf")