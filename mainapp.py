#!/usr/bin/python2.7 
#coding:utf-8
"""
@description:a sublime text plugin used post code to a share library
"""
from settings import route_app,render,filter_html,logger
import web
import cgi
import codestore
import os
import apiapp
import codeapp
import groupapp

web.config.debug = True

cgi.maxlen = 10 * 1024 * 1024 # 10MB

""" application defined """
app  = route_app()
app.mount("/api",apiapp.app)
app.mount("/code",codeapp.app)
app.mount("/group",groupapp.app)

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
        tops = codestore.list_index(limit=50) 
        langs = codestore.list_langs()
        return render("index.html",tops = tops,langs=langs) 



@app.route("/search")
class code_search():
    def POST(self):
        return None     


class GEventServer():
    """ gevent wsgi服务器定义，可利用多进程
    """
    def __init__(self,handler):
        self.handler = handler

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
    try:
        with open("/var/run/talkincode.pid",'wb') as pidfs:
            pidfs.write(str(os.getpid()))     
        GEventServer(app.wsgifunc()).start()
    except:
        app.run()

