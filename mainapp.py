#!/usr/bin/python2.7 
#coding:utf-8
"""
@description:a sublime text plugin used post code to a share library
"""
import urllib, hashlib
from settings import route_app,render
from settings import errorpage,logger
from settings import config,pagesize
from tools import convtime
import web
import cgi
import apiapp
import codeapp
import newsapp
import userapp
import tagsapp
import opensapp
import store
import markdown


cgi.maxlen = 10 * 1024 * 1024 # 10MB

""" application defined """
app  = route_app()
app.mount("/api",apiapp.app)
app.mount("/code",codeapp.app)
app.mount("/open",opensapp.app)
app.mount("/news",newsapp.app)
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

def get_avatar(email=None,size=40):
    default = "http://www.talkincode.org/static/img/avatar.gif"    
    if not email:
        return default
    # Set your variables here

    # construct the url
    gravatar_url = "http://www.gravatar.com/avatar/" + hashlib.md5(email.lower()).hexdigest() + "?"
    gravatar_url += urllib.urlencode({'d':default, 's':str(size)})
    return gravatar_url

def context_hook():
    web.ctx.config = config
    web.ctx.pagesize = pagesize
    web.ctx.session = session
    web.ctx.md = made
    web.ctx.convtime=convtime
    web.ctx.get_avatar = get_avatar
    web.ctx.get_user=store.get_user
app.add_processor(web.loadhook(context_hook))   


@app.route("/index")
class home():
    def GET(self):
        web.header("Content-Type","text/html; charset=utf-8")
        raise web.seeother("/",absolute=True)
            

@app.route("/group/(.*)")
class js():
    def GET(self,xpath):
        raise web.seeother("/news/%s"%xpath,absolute=True)

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
        tops = store.Code.where().order_by("create_time desc")[:10] 
        langs = store.Lang.where()
        stats = store.get_post_stats(False)
        posts = store.Post.where(status=1).order_by("created desc")[:pagesize]
        codetags = store.get_code_tags(30)
        posttags =  store.get_post_tags(30)
        return render("index.html",
            tops = tops,
            posts=posts,
            langs=langs,
            stats=stats,
            codetags=codetags,
            posttags=posttags) 


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
        web.header("Content-Type","text/html; charset=utf-8")
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
    def GET(self):
        web.header("Content-Type","text/html; charset=utf-8")
        q = web.input().get("q")
        qstr = "http://www.google.com/search?q=site:talkincode.org %s"%q
        raise web.seeother(qstr)

@app.route("/sitemaps.xml")
class sitemaps():
    def GET(self):
        '''sitemaps'''
        web.header("Content-Type","text/xml; charset=utf-8")
        urls = store.sitemap_data()
        return render("sitemaps.xml",urls=urls)

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
        server = WSGIServer((self.host, self.port), self.handler)
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

web.config.debug = False

#application = app.wsgifunc()        

# def start_server(port=19000):
#     logger.info('starting server %s'%port)
#     GEventServer(application,"0.0.0.0",port).start()

if __name__ == "__main__":
    import  platform
    if  platform.system() == "Windows":
        web.config.debug = False
        app.run()
    # else:
    #     start_server()


    

