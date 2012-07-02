#!/usr/bin/python2.7 
#coding:utf-8
"""
@description:a sublime text plugin used post code to a share library
"""
from settings import route_app,render,logger,filter_html
import web
import cgi
# import datetime
import store
import json
import os

web.config.debug = True

cgi.maxlen = 10 * 1024 * 1024 # 10MB

""" application defined """
app  = route_app()

'''session defined'''
# session = web.session.Session(app, web.session.DiskStore('sessions'), {'count': 0})   
if web.config.get('_session') is None:
   session = web.session.Session(app, web.session.DiskStore('sessions'), {'count': 0})
   web.config._session = session
else:
   session = web.config._session

def session_hook():
    web.ctx.session = session

app.add_processor(web.loadhook(session_hook))   

def notfound():
    return web.notfound("Sorry, the page you were looking for was not found.")

def errorpage(msg):
    return render("error.html",error=msg) 

@app.route("/index")
class home():
    def GET(self):
        raise web.seeother("/",absolute=True)

@app.route("/")
class index():
    def GET(self):
        tops = store.list_index(limit=50) 
        if tops:
            content = store.get_content(tops[0]['id'])
            if content:
                content["content"] = filter_html(content["content"]) 
                return render("index.html",tops = tops,content=content) 
            else:
                return render("error.html",error="no data") 

               

@app.route("/about")
class about():
    def GET(self):
        raise web.seeother("/",absolute=True)

@app.route("/contact")
class contact():
    def GET(self):
        raise web.seeother("/",absolute=True)                

@app.route("/js/(.*)")
class js():
    def GET(self,filename):
        raise web.seeother("/static/js/%s"%filename,absolute=True)

@app.route("/css/(.*)")
class css():
    def GET(self,filename):
        raise web.seeother("/static/css/%s"%filename,absolute=True)

@app.route("/img/(.*)")
class img():
    def GET(self,filename):
        raise web.seeother("/static/img/%s"%filename,absolute=True)        



@app.route("/code/add")
class code_add():
    def POST(self):
        forms = web.input()
        params = dict(title = forms.get("title"),
                      auther = forms.get("auther"),
                      email = forms.get("email"),
                      tags = forms.get("tags"),
                      content = forms.get("content"),
                      authkey = forms.get("authkey"),
                      filename = forms.get("filename"),
                      lang=forms.get("lang"))
        try:
            store.add_code(**params)
            return "ok"
        except:
            return errorpage("error")

@app.route("/code/index")
class code_index():
    def GET(self):
        keyword = web.input().get("keyword") or ''
        limit = web.input().get("limit") or 1000

        try:
            tops = store.list_index(keyword=keyword,limit=limit) 
            return json.dumps(tops)
        except Exception,e:
            logger.error("query data error %s"%e)
            return json.dumps({"error":"query data error "})         

@app.route("/code/get/(.*)")
class code_get():
    def GET(self,uid):
        try:
            content = store.get_content(uid)
            return json.dumps(content)
        except:
            return json.dumps({"error":"query data error"})  


@app.route("/search")
class code_search():
    def POST(self):
        keyword = web.input().get("keyword")
        if not keyword:
            raise web.seeother("/")
        tops = store.list_index(keyword=keyword,limit=50) 
        if tops:
            content = store.get_content(str(tops[0]['id']))
            if content:
                content["content"] = filter_html(content["content"]) 
                return render("index.html",tops = tops,content=content) 
            else:
                return render("error.html",error="no data")          

@app.route("/code/view/(.*)")
class code_view():
    def GET(self,uid):
        tops = store.list_index(limit=50) 
        content = store.get_content(uid)
        if content:
            content["content"] = filter_html(content["content"]) 
            return render("index.html",tops = tops,content=content,pagename=content["title"]) 
        else:
            return render("error.html",error="no data") 



if __name__ == "__main__":
    # app.run()
    try:
        with open("/var/run/talkincode.pid",'wb') as pidfs:
            pidfs.write(str(os.getpid()))
        import tornado.web
        import tornado.wsgi
        import tornado.ioloop
        import tornado.httpserver
        # from tornado.options import options,define,parse_command_line    
        tornado_wsgi = tornado.wsgi.WSGIContainer(app.wsgifunc())
        tornado_app = tornado.web.Application([
        ('.*', tornado.web.FallbackHandler, dict(fallback=tornado_wsgi)),
        ])
        tornado_serv = tornado.httpserver.HTTPServer(tornado_app)
        tornado_serv.listen(18000)
        tornado.ioloop.IOLoop.instance().start()            
    except:
        app.run()

