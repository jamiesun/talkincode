#!/usr/bin/python2.7 
#coding:utf-8
from settings import route_app,render,pagesize
import store

import web

app  = route_app()

@app.route("")
class routeto():
    def GET(self):
        raise web.seeother("/tags/",absolute=True)

@app.route("/")
class index():
    def GET(self):
        web.header("Content-Type","text/html; charset=utf-8")
        return render("tags.html") 

@app.route("/list/(.*)")
class index():
    def GET(self,tag):
        web.header("Content-Type","text/html; charset=utf-8")
        langs = store.Lang.where()
        posts = store.Post.where("tags like %s",'%%%s%%'%tag)[:50]
        codes = store.Code.where("tags like %s",'%%%s%%'%tag)[:50]
        tags = store.get_tags(30)
        return render("tags_list.html",
            langs = langs,
            posts=posts,
            codes=codes,
            tags=tags) 
