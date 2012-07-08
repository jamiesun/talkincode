#!/usr/bin/python2.7 
#coding:utf-8
from settings import route_app,filter_html,render
import tagstore
import groupstore
import codestore
import web

app  = route_app()

@app.route("")
class routeto():
    def GET(self):
        raise web.seeother("/tags/",absolute=True)

@app.route("/")
class index():
    def GET(self):
        return render("tags.html") 

@app.route("/list/(.*)")
class index():
    def GET(self,tag):
        langs = codestore.list_langs()   
        posts = groupstore.list_posts_by_tag(tag)  
        codes = codestore.list_codes_bytags(tag)
        tags = tagstore.get_tags()
        return render("tags_list.html",
            langs = langs,
            posts=posts,
            codes=codes,
            tags=tags) 
