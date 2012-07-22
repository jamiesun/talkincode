#!/usr/bin/python2.7 
#coding:utf-8
from settings import route_app,render,pagesize
from settings import errorpage
from tools import filter_html
import store
import web

langextset = {'c': 'c', 'java': 'java', 'lisp': 'lsp', "shell":"sh",
              'javascript': 'js', 'c++': 'cpp', 'perl': 'pl',
               'python': 'py', 'pascal': 'pas', 'sql': 'sql',
                'php': 'php', 'ruby': 'rb','css':'css','html':'html'}

app  = route_app()

@app.route("")
class routeto():
    def GET(self):
        raise web.seeother("/code/",absolute=True)

@app.route("/")
class index():
    def GET(self):
        web.header("Content-Type","text/html; charset=utf-8")
        page = int(web.input().get("page",1)) 
        offset = (page-1) * 50  
        langs = store.Lang.where()
        tags = store.get_code_tags(30)
        tops = store.Code.where().order_by("create_time desc")[offset:50]
        return render("code.html",tops = tops,langs=langs,tags=tags,page=page) 

@app.route("/add")
class add_code():
    def GET(self):
        web.header("Content-Type","text/html; charset=utf-8")
        langs = store.Lang.where()
        return render("code_add.html",langs = langs)

    def POST(self):
        user = web.ctx.session.get("user")
        author = user and user.author or 'Anonymous'
        email = user and user.email or '@'
        form = web.input()
        title = form.get("title")
        tags = form.get("tags",'other')
        lang = form.get("lang","undefined")
        content = form.get("content")

        if not title:
            raise 'title can not empty'

        if not content:
            raise 'content can not empty'

        try:
            if tags :tags = tags[:255]
            title = title[:255]
            code = store.Code(
                        id = store.nextid(),
                        title=title,
                        lang=lang,
                        author=author,
                        email=email,
                        tags=tags,
                        content=content,
                        create_time=store.currtime())
            code.save()
            raise web.seeother("/code/",absolute=True)
        except Exception, e:
            return errorpage("add code error %s"%e)



@app.route("/comment/add")
class add_comment():
    def POST(self):
        try:
            comment = store.Comment()
            comment.id = store.nextid()
            user = web.ctx.session.get("user")
            comment.userid = user and user.id or ''  
            form = web.input()
            comment.author = user and user.username or form.get("author")[:64]
            comment.content = form.get("content")
            comment.postid = form.get("postid")
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
            raise web.seeother("/code/view/%s"%comment.postid,absolute=True)
        except Exception, e:
            import traceback
            traceback.print_exc()
            return errorpage("add comment error %s"%e)    


@app.route("/category/(.*)")
class index_cat():
    def GET(self,lang):
        web.header("Content-Type","text/html; charset=utf-8")
        page = int(web.input().get("page",1)) 
        offset = (page-1) * 50  
        langs = store.Lang.where()
        tags = store.get_code_tags(30)
        tops =  store.Code.where().order_by("create_time desc")[offset:50]
        return render("code.html",
            tops = tops,
            tags=tags,
            page=page,
            langs=langs)    


@app.route("/tag/(.*)")
class index_cat():
    def GET(self,tag):
        web.header("Content-Type","text/html; charset=utf-8")
        page = int(web.input().get("page",1)) 
        offset = (page-1) * 50  
        tags = store.get_code_tags(30)
        langs = store.Lang.where()
        tops = store.Code.where("tags like %s",'%%%s%%'%tag).order_by("create_time desc")[offset:50]
        return render("code.html",
            tops=tops,
            page=page,
            tags=tags,
            langs=langs)                     


@app.route("/view/(.*)")
class code_view():
    def GET(self,uid):
        web.header("Content-Type","text/html; charset=utf-8")
        try:
            page = int(web.input().get("page",1)) 
            offset = (page-1) * 50  
            versions = store.Code.where(parent=uid) [offset:50]
            content = store.Code.get(id=uid)
            content.hits += 1
            content.save()
            posts = store.Post.where(codeid=uid)
            comments = store.Comment.where(postid=uid).order_by("created desc")[(page-1)*pagesize:pagesize]
            content.content = filter_html(content.content) 
            return render("code_view.html",
                page=page,
                versions = versions,
                content=content,
                comments=comments,
                pagename=content.title,
                posts=posts) 
        except:
            return render("error.html",error="no data")        



@app.route("/download/(.*)")
class code_view():
    def GET(self,uid):
        try:
            content = store.Code.get(uid)
            web.header("Content-Disposition","attachment; filename='%s.%s'"\
                %(uid,langextset.get(content.lang,"txt")))
            return content.content
        except:
            return render("error.html",error="no data")    

@app.route("/rec/(.*)")
class index():
    def GET(self,uid):
        web.header("Content-Type","text/html; charset=utf-8")
        code = store.Code.get(uid)
        try:
            if code:
                code.recs += 1
                code.save()
        except:
            pass
        raise web.seeother("/code/",absolute=True)