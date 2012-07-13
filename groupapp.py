#!/usr/bin/python2.7 
#coding:utf-8
from settings import route_app,filter_html,render,logger
from settings import errorpage,auth_user
import tagstore
import groupstore
import codestore
import web

app  = route_app()

@app.route("")
class routeto():
    def GET(self):
        raise web.seeother("/group/",absolute=True)

@app.route("/")
class index():
    def GET(self):
        web.header("Content-Type","text/html; charset=utf-8")
        page = int(web.input().get("page",1)) 
        stats = groupstore.get_post_stats(False)
        tops = groupstore.list_posts(page=page)
        tags = tagstore.get_post_tags()
        return render("group.html",
            tops = tops,
            stats=stats,
            tags=tags,
            page=page) 

@app.route("/tag/(.*)")
class index():
    def GET(self,tag):
        web.header("Content-Type","text/html; charset=utf-8")
        page = int(web.input().get("page",1)) 
        tags = tagstore.get_post_tags()
        stats = groupstore.get_post_stats(tag)
        tops = groupstore.list_posts_by_tag(tag,page=page)
        return render("group.html",
            ctag=tag,
            tops = tops,
            stats=stats,
            tags=tags,
            page=page) 

@app.route("/post/add")
class add_post():
    @auth_user
    def GET(self):
        web.header("Content-Type","text/html; charset=utf-8")
        codeid = web.input().get("codeid")
        return render("post_add.html",codeid=codeid) 

    @auth_user
    def POST(self):
        user = web.ctx.session.get("user")
        form = web.input()
        codeid = form.get("codeid")
        title = form.get("title")
        tags = form.get("tags")
        content = form.get("content")
        userid = user["id"]
        if not title  or not content:
            return errorpage(u"请输入完整数据")
        try:
            if tags :tags = tags[:255]
            title = title[:255]
            groupstore.add_post(userid,title,tags,content,codeid)
            raise web.seeother("/group/",absolute=True)
        except Exception, e:
            return errorpage("add post error %s"%e)

@app.route("/comment/add")
class add_comment():
    def POST(self):
        try:
            user = web.ctx.session.get("user")
            userid = user and user["id"] or None  
            form = web.input()
            author = user and user["username"] or form.get("author")
            content = form.get("content")
            postid = form.get("postid")
            email = user and user["email"] or form.get("email")
            url =  user and user["url"] or form.get("url")
            ip = web.ctx.ip
            agent =  web.ctx.env.get('HTTP_USER_AGENT')
            status = userid and 1 or 0
            if author : author = author[:64]
            if email :email = email[:128]
            if url : url = url[:128]

            if not content:
                raise Exception('content not empty')
            if not userid:
                if not author or not email :
                    raise Exception('author email not empty') 
            groupstore.add_comment(postid,content,userid,author,email,url,ip,agent,status)
            raise web.seeother("/group/post/view/%s"%postid,absolute=True)
        except Exception, e:
            return errorpage("add comment error %s"%e)    


@app.route("/post/update")
class update_post():
    @auth_user
    def GET(self):
        pass

@app.route("/post/view/(.*)")
class get_post():
    def GET(self,uid):
        web.header("Content-Type","text/html; charset=utf-8")
        try:
            page = int(web.input().get("page",1)) 
            post = groupstore.get_content(uid)
            tags = tagstore.get_post_tags()
            codeid = post.get("codeid")
            code = None
            if codeid:
                code = codestore.get_content(codeid)
            comments = groupstore.list_comments(uid,page=page)
            return render("post_view.html",
                tags=tags,
                post=post,
                comments=comments,
                page=page,
                code=code,
                pagename=post.get('title'))
        except Exception,e:
            return errorpage("error %s"%e)
