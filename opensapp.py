#!/usr/bin/python2.7 
#coding:utf-8
from settings import route_app,render,pagesize,errorpage
import store 
import web

app  = route_app()

@app.route("")
class routeto():
    def GET(self):
        raise web.seeother("/open/",absolute=True)

@app.route("/")
class index():
    def GET(self):
        web.header("Content-Type","text/html; charset=utf-8")
        page = int(web.input().get("page",1)) 
        offset = (page-1)*pagesize
        tags = store.get_project_tags(20)
        projs = store.Project.where().order_by("created desc")[offset:pagesize]
        return render("project.html",
            projs = projs,
            tags=tags,
            page=page) 

@app.route("/tag/(.*)")
class index():
    def GET(self,tag):
        web.header("Content-Type","text/html; charset=utf-8")
        page = int(web.input().get("page",1)) 
        offset = (page-1)*pagesize
        tags = store.get_project_tags(20)
        projs = store.Project.where("tags like %s",'%%%s%%'%tag).order_by("created desc")[offset:pagesize]
        return render("project.html",
            projs = projs,
            tags=tags,
            page=page)         

@app.route("/proj/(.*)")
class project():
    def GET(self,uid):
        web.header("Content-Type","text/html; charset=utf-8")
        page = int(web.input().get("page",1)) 
        offset = (page-1)*pagesize
        try:
            proj = store.Project.get(uid)
            proj.hits += 1
            proj.save()
            comments = store.Comment.where(postid=uid).order_by("created desc")[offset:pagesize]
            return render("project_view.html",
                proj = proj,
                comments=comments,
                page=page)  
        except Exception, e:
            return errorpage("view project error %s"%e)



@app.route("/proj/rec/(.*)")
class rec():
    def GET(self,uid):
        web.header("Content-Type","text/html; charset=utf-8")
        proj = store.Project.get(uid)
        try:
            if proj:
                proj.recs += 1
                proj.save()
        except:
            pass
        raise web.seeother("/open/",absolute=True)

@app.route("/comment/add")
class add_comment():
    def POST(self):
        try:
            comment = store.Comment()
            comment.id = store.nextid()
            user = web.ctx.session.get("user")
            comment.userid = user and user.id or ''  
            form = web.input()
            comment.postid = form.get("postid")
            comment.author = user and user.username or form.get("author")[:64]
            comment.content = form.get("content")
            comment.email = user and user.email or form.get("email")[:128]
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
            raise web.seeother("/open/proj/%s"%comment.postid,absolute=True)
        except Exception, e:
            return errorpage("add comment error %s"%e)    

@app.route("/proj/add")
class add_proj():
    def GET(self):
        web.header("Content-Type","text/html; charset=utf-8")
        return render("project_add.html",langs=store.Lang.where()) 

    def POST(self):
        proj = store.Project(id=store.nextid())
        form = web.input()
        proj.image = form.get("image","/static/img/project.jpg")
        proj.name = form.get("title")
        proj.owner = form.get("owner")
        proj.license = form.get("license",'unknow')
        proj.homepage = form.get("homepage")
        proj.tags = form.get("tags",'other')[:255]
        proj.description = form.get("content")
        proj.lang = form.get("lang",'undefined')
        proj.created = store.currtime()

        if not proj.name  or not proj.description:
            return errorpage(u"标题和内容不能为空")

        if not proj.owner:
            return errorpage(u"所有者不能为空")   

        if not proj.homepage:
            return errorpage(u"项目主页不能为空")   

        try:
            proj.save()
            raise web.seeother("/open/",absolute=True)
        except Exception, e:
            return errorpage("add project error %s"%e)
