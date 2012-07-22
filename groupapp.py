#!/usr/bin/python2.7 
#coding:utf-8
from settings import route_app,render,pagesize
from settings import errorpage,auth_user
import store
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
        offset = (page-1)*pagesize
        stats = store.get_post_stats(False)
        tops = store.Post.where().order_by("modified desc")[offset:pagesize]
        tags = store.get_post_tags(30)
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
        offset = (page-1)*pagesize
        tags = store.get_post_tags(30)
        stats = store.get_post_stats(tag)
        tops = store.Post.where("tags like %s",'%%%s%%'%tag).order_by("modified desc")[offset:pagesize]
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
        post = store.Post(id=store.nextid())
        user = web.ctx.session.get("user")
        form = web.input()
        post.codeid = form.get("codeid")
        post.title = form.get("title")
        post.tags = form.get("tags","other")[:255]
        post.content = form.get("content")
        post.userid = user.id
        post.created = post.modified = store.currtime()
        if not post.title  or not post.content:
            return errorpage(u"请输入完整数据")
        try:
            post.save()
            raise web.seeother("/group/",absolute=True)
        except Exception, e:
            return errorpage("add post error %s"%e)

@app.route("/comment/add")
class add_comment():
    def POST(self):
        try:
            comment = store.Comment()
            comment.id = store.nextid()
            user = web.ctx.session.get("user")
            comment.userid = user and user.id or ''  
            form = web.input()
            comment.author = user and user.username or form.get("author")
            comment.content = form.get("content")
            comment.postid = form.get("postid")
            comment.email = user and user.email or form.get("email")
            comment.url =  user and user.url or form.get("url")
            comment.ip = web.ctx.ip
            comment.agent =  web.ctx.env.get('HTTP_USER_AGENT')
            comment.status = comment.userid and 1 or 0
            comment.created = store.currtime()

            if not comment.content:
                raise Exception('content not empty')
            if not comment.userid:
                if not comment.author or not comment.email :
                    raise Exception('author email not empty') 
            comment.save()
            store.Comment.commit()
            raise web.seeother("/group/post/view/%s"%comment.postid,absolute=True)
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
            post = store.Post.get(uid)
            post.hits += 1
            post.save()
            tags = store.get_post_tags(30)
            codeid = post.codeid
            code = None
            if codeid:
                code = store.Code.get(codeid)
            comments = store.Comment.where(postid=uid).order_by("created desc")[(page-1)*pagesize:pagesize]
            return render("post_view.html",
                tags=tags,
                post=post,
                comments=comments,
                page=page,
                code=code,
                pagename=post.get('title'))
        except Exception,e:
            return errorpage("error %s"%e)


@app.route("/post/rec/(.*)")
class index():
    def GET(self,uid):
        web.header("Content-Type","text/html; charset=utf-8")
        post = store.Post.get(uid)
        try:
            if post:
                post.recs += 1
                post.save()
        except:
            pass
        raise web.seeother("/group/",absolute=True)