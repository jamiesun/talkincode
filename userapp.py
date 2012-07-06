#!/usr/bin/python2.7 
#coding:utf-8
from settings import route_app,filter_html,render
import userstore
import web

app  = route_app()

@app.route("")
class routeto():
    def GET(self):
        raise web.seeother("/user/",absolute=True)

@app.route("/")
class index():
    def GET(self):
        return render("user.html") 

@app.route("/settings")
class index():
    def GET(self):
        session = web.ctx.session
        user = session.get("user")
        if not user:
            raise web.seeother("/")
        userobj = userstore.get_user(user["username"])
        return render("user_settings.html",user=userobj) 


