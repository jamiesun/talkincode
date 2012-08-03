#!/usr/bin/python2.7 
#coding:utf-8
import datetime
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
from mako.lookup import TemplateLookup 
from mako import exceptions
import web
import logging
import sys
import markdown


md = markdown.Markdown(safe_mode='escape')
appdir = "./"

config = {
  "sitename":"Talk in code"
}

""" define logging """
logger = logging.getLogger("talkincode")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
file_handler = logging.FileHandler("%s/logs/server.log"%appdir)
console_handler = logging.StreamHandler(sys.stderr)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

class route_app(web.application): 
    def mount(self,pattern,app):
        self.add_mapping(pattern, app)     
    def route(self, *args): 
        def wrapper(cls): 
            for pattern in args: 
                self.add_mapping(pattern, cls) 
            return cls 
        return wrapper



""" define memary CacheManager imp """
memary_manager = CacheManager(cache_regions={
    'short_term':{
        'type': 'memory',
        'expire': 3600
    },
})

""" define file CacheManager imp """
cache = CacheManager(**parse_cache_config_options({
    'cache.type': 'file',
    'cache.data_dir': '%s/cache/data'%appdir,
    'cache.lock_dir': '%s/cache/lock'%appdir
}))   

_lookup = TemplateLookup(directories=['%s/templates'%appdir],
                          input_encoding='utf-8',
                          output_encoding='utf-8',
                          encoding_errors='replace',
                          module_directory="%s/tmp"%appdir,
                          cache_impl='beaker',
                          cache_args={'manager':memary_manager } )  

pagesize = 20



def render(filename,**args):
    """ define mako render function """
    try:
        mytemplate = _lookup.get_template(filename) 
        args["sitename"] = config.get("sitename")
        args["cdate"] = datetime.datetime.now().strftime( "%Y-%m-%d")
        args['session'] = web.ctx.session 
        args["ctx"] = web.ctx
        return mytemplate.render(**args)
    except:
        return exceptions.text_error_template().render()

def notfound():
    return web.notfound("Sorry, the page you were looking for was not found.")

def errorpage(msg):
    web.header("Content-Type","text/html; charset=utf-8")
    return render("error.html",error=msg)        

    
def auth_user(func):
    def warp(*args,**kwargs):
        session = web.ctx.session 
        if not session or not session.get("user"):
            raise web.seeother("/login",absolute=True)
        else:
            return func(*args,**kwargs)
    return warp

def auth_admin(func):
    def warp(*args,**kwargs):
        session = web.ctx.session 
        if not session or not session.get("user"):
            raise web.seeother("/login",absolute=True)
        elif session.get("user").role == 0:
            raise web.seeother("/",absolute=True)
        else:
            return func(*args,**kwargs)
    return warp



if __name__ == "__main__":
    pass


