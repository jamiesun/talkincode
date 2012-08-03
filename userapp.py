#!/usr/bin/python2.7 
#coding:utf-8
from settings import route_app,render
import store
import web

app  = route_app()

@app.route("")
class routeto():
    def GET(self):
        raise web.seeother("/user/",absolute=True)

@app.route("/")
class index():
    def GET(self):
        web.header("Content-Type","text/html; charset=utf-8")
        return render("user.html") 

@app.route("/settings")
class index():
    def GET(self):
        web.header("Content-Type","text/html; charset=utf-8")
        session = web.ctx.session
        user = session.get("user")
        if not user:
            raise web.seeother("/")
        userobj = store.User.get(username=user.username)
        return render("user_settings.html",user=userobj) 


