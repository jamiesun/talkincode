#!/usr/bin/python2.7 
#coding:utf-8
"""
@description:a sublime text plugin used post code to a share library
"""
from settings import route_app,render,logger
from settings import errorpage
from store import get_conn
from settings import config,pagesize
import web
import cgi
import codestore
import groupstore
import os
import apiapp
import codeapp
import groupapp
import userapp
import tagsapp
import store
import tagstore
import markdown


cgi.maxlen = 10 * 1024 * 1024 # 10MB

""" application defined """
app  = route_app()
app.mount("/api",apiapp.app)
app.mount("/code",codeapp.app)
app.mount("/group",groupapp.app)
app.mount("/user",userapp.app)
app.mount("/tags",tagsapp.app)
'''session defined'''
# session = web.session.Session(app, web.session.DiskStore('sessions'), {'count': 0})   
if web.config.get('_session') is None:
   session = web.session.Session(app, web.session.DiskStore('sessions'), {'count': 0})
   web.config._session = session
else:
   session = web.config._session

made = markdown.Markdown(safe_mode='escape')
def context_hook():
    web.ctx.config = config
    web.ctx.pagesize = pagesize
    web.ctx.session = session
    web.ctx.db = get_conn
    web.ctx.md = made
    web.ctx.get_user=groupstore.get_user
    web.ctx.get_group=groupstore.get_group
app.add_processor(web.loadhook(context_hook))   


@app.route("/index")
class home():
    def GET(self):
        web.header("Content-Type","text/html; charset=utf-8")
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

@app.route("/")
class index():
    def GET(self):
        web.header("Content-Type","text/html; charset=utf-8")
        tops = codestore.list_index(limit=5) 
        langs = codestore.list_langs()
        stats = groupstore.get_post_stats()
        posts = groupstore.list_posts(limit=20)
        tagset = tagstore.get_tags()
        return render("index.html",
            tops = tops,
            posts=posts,
            langs=langs,
            stats=stats,
            tagset=tagset) 

@app.route("/join")
class register():
    def GET(self):
        web.header("Content-Type","text/html; charset=utf-8")
        return render("join.html") 

    def POST(self):
        form = web.input()
        username = form.get("username")
        password = form.get("password")
        password2 = form.get("password2")
        email = form.get("email")
        if not username or not password:
            return errorpage(u"用户名和密码不能为空") 
        if not password == password2:
            return errorpage(u"确认密码错误")
        if not email:
            return errorpage(u"电子邮件不能为空")

        try:
            user = store.register(username,password,email)
            usession = web.ctx.session
            usession["user"] = user 
            raise web.seeother("/")
        except Exception,e:
            return errorpage("register error %s"%e)

@app.route("/login")
class login():
    def GET(self):
        return render("login.html") 

    def POST(self):
        form = web.input()
        username = form.get("username")
        password = form.get("password")
        if not username or not password:
            return errorpage(u"用户名和密码不能为空") 
        try:
            user = store.login(username,password)
            usession = web.ctx.session
            usession["user"] = user 
            raise web.seeother("/")
        except Exception,e:
            return errorpage("login error %s"%e)


@app.route("/logout")
class login():
    def GET(self):
        sess = web.ctx.session
        sess["user"] = None
        raise web.seeother("/")

@app.route("/search")
class code_search():
    def POST(self):
        return None     


class GEventServer():
    """ gevent wsgi服务器定义，可利用多进程
    """
    def __init__(self,handler,host,port):
        self.handler = handler
        self.host = host
        self.port = port


    def start(self):
        from multiprocessing import Process
        from gevent import monkey
        monkey.patch_socket()
        monkey.patch_os()
        from gevent.wsgi import WSGIServer
        server = WSGIServer((self.host, self.port), self.handler,log=None)
        server.pre_start()
        def serve_forever():
            logger.info('starting server')
            try:
                server.start_accepting()

                try:
                    server._stopped_event.wait()
                except:
                    raise
            except KeyboardInterrupt:
                pass                
        for i in range(2):
            Process(target=serve_forever, args=tuple()).start()
        serve_forever()

if __name__ == "__main__":
    web.config.debug = False

    try:
        with open("/var/run/talkincode.pid",'wb') as pidfs:
            pidfs.write(str(os.getpid()))     
        GEventServer(app.wsgifunc(),"0.0.0.0",18000).start()
    except Exception,e:
        import traceback
        logger.info("gevent server start fail %s"%traceback.format_exc())
        app.run()

