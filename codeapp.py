#!/usr/bin/python2.7 
#coding:utf-8
from settings import route_app,filter_html,render
import codestore
import web

app  = route_app()

@app.route("")
class routeto():
    def GET(self):
        raise web.seeother("/code/",absolute=True)

@app.route("/")
class index():
    def GET(self):
        langs = codestore.list_langs()
        tops = codestore.list_index(limit=50) 
        return render("code.html",tops = tops,langs=langs) 


@app.route("/view/(.*)")
class code_view():
    def GET(self,uid):
        tops = codestore.list_index(limit=50) 
        content = codestore.get_content(uid)
        if content:
            content["content"] = filter_html(content["content"]) 
            return render("code_view.html",tops = tops,content=content,pagename=content["title"]) 
        else:
            return render("error.html",error="no data")        


@app.route("/search")
class code_search():
    def POST(self):
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