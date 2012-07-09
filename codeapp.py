#!/usr/bin/python2.7 
#coding:utf-8
from settings import route_app,filter_html,render,auth_user
from settings import errorpage
import codestore
import groupstore
import web

app  = route_app()

@app.route("")
class routeto():
    def GET(self):
        raise web.seeother("/code/",absolute=True)

@app.route("/")
class index():
    def GET(self):
        page = int(web.input().get("page",1)) 
        langs = codestore.list_langs()
        tops = codestore.list_index(page=page) 
        return render("code.html",tops = tops,langs=langs,page=page) 

@app.route("/add")
class add_code():
    @auth_user
    def GET(self):
        langs = codestore.list_langs()
        return render("code_add.html",langs = langs)

    @auth_user
    def POST(self):
        user = web.ctx.session.get("user")
        form = web.input()
        title = form.get("title")
        tags = form.get("tags")
        lang = form.get("lang")
        content = form.get("content")

        if not title or not lang or not content:
            return errorpage(u"请输入完整数据")
        try:
            if tags :tags = tags[:255]
            title = title[:255]
            params = dict(title=title,
                        lang=lang,
                        author=user["username"],
                        email=user["email"],
                        tags=tags,
                        content=content)
            codestore.add_code(**params)
            raise web.seeother("/code/",absolute=True)
        except Exception, e:
            return errorpage("add code error %s"%e)


@app.route("/category/(.*)")
class index_cat():
    def GET(self,lang):
        page = int(web.input().get("page",1)) 
        langs = codestore.list_langs()
        tops = codestore.list_codes_bylang(lang,page=page) 
        return render("code.html",
            tops = tops,
            page=page,
            langs=langs)         


@app.route("/view/(.*)")
class code_view():
    def GET(self,uid):
        versions = codestore.list_versions(uid) 
        content = codestore.get_content(uid)
        posts = groupstore.list_posts_by_codeid(uid)
        if content:
            content["content"] = filter_html(content["content"]) 
            return render("code_view.html",
                versions = versions,
                content=content,
                pagename=content["title"],
                posts=posts) 
        else:
            return render("error.html",error="no data")        


@app.route("/search")
class code_search():
    def POST(self):
        page = int(web.input().get("page",1)) 
        keyword = web.input().get("keyword")
        if not keyword:
            raise web.seeother("/")
        tops = codestore.list_index(keyword=keyword,limit=50) 
        if tops:
            content = codestore.get_content(str(tops[0]['id']))
            if content:
                content["content"] = filter_html(content["content"]) 
                return render("index.html",tops = tops,content=content) 
            else:
                return render("error.html",error="no data") 