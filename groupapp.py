#!/usr/bin/python2.7 
#coding:utf-8
from settings import route_app,filter_html,render
import codestore
import groupstore
import web

app  = route_app()

@app.route("")
class routeto():
    def GET(self):
        raise web.seeother("/group/",absolute=True)

@app.route("/")
class index():
    def GET(self):
        tops = codestore.list_index(limit=50) 
        groups = groupstore.list_groups()
        return render("group.html",tops = tops,groups=groups) 



