#!/usr/bin/python2.7 
#coding:utf-8
from settings import route_app,filter_html,render,auth_user
from settings import errorpage
import codestore
import groupstore
import tagstore
import web

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
        langs = codestore.list_langs()
        tags = tagstore.get_code_tags()
        tops = codestore.list_index(page=page,limit=50) 
        return render("code.html",tops = tops,langs=langs,tags=tags,page=page) 

@app.route("/add")
class add_code():
    def GET(self):
        web.header("Content-Type","text/html; charset=utf-8")
        langs = codestore.list_langs()
        return render("code_add.html",langs = langs)

    def POST(self):
        user = web.ctx.session.get("user")
        author = user and user['author'] or 'Anonymous'
        email = user and user['email'] or 'Anonymous@talkincode.org'
        form = web.input()
        title = form.get("title")
        tags = form.get("tags")
        lang = form.get("lang","undefined")
        content = form.get("content")

        try:
            if tags :tags = tags[:255]
            title = title[:255]
            params = dict(title=title,
                        lang=lang,
                        author=author,
                        email=email,
                        tags=tags,
                        content=content)
            codestore.add_code(**params)
            raise web.seeother("/code/",absolute=True)
        except Exception, e:
            return errorpage("add code error %s"%e)

@app.route("/comment/add")
class add_comment():
    def POST(self):
        try:
            user = web.ctx.session.get("user")
            userid = user and user["id"] or None  
            form = web.input()
            author = user and user["username"] or form.get("author")
            content = form.get("content")
            codeid = form.get("codeid")
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
            codestore.add_comment(codeid,content,userid,author,email,url,ip,agent,status)
            raise web.seeother("/code/view/%s"%codeid,absolute=True)
        except Exception, e:
            return errorpage("add comment error %s"%e)    


@app.route("/category/(.*)")
class index_cat():
    def GET(self,lang):
        web.header("Content-Type","text/html; charset=utf-8")
        page = int(web.input().get("page",1)) 
        langs = codestore.list_langs()
        tags = tagstore.get_code_tags()
        tops = codestore.list_codes_bylang(lang,page=page,limit=50) 
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
        tags = tagstore.get_code_tags()
        langs = codestore.list_langs()
        tops = codestore.list_codes_bytags(tag,page=page,limit=50) 
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
            versions = codestore.list_versions(uid) 
            content = codestore.get_content(uid)
            posts = groupstore.list_posts_by_codeid(uid)
            comments = groupstore.list_comments(uid,page=page)
            content["content"] = filter_html(content["content"]) 
            return render("code_view.html",
                page=page,
                versions = versions,
                content=content,
                comments=comments,
                pagename=content["title"],
                posts=posts) 
        except:
            return render("error.html",error="no data")        


@app.route("/search")
class code_search():
    def POST(self):
        pass