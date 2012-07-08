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
import re
import markdown
md = markdown.Markdown(safe_mode='escape')

config = {
  "sitename":"Talk in code"
}

""" define logging """
logger = logging.getLogger("sayincode")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S',)
file_handler = logging.FileHandler("./logs/server.log")
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
    'cache.data_dir': './cache/data',
    'cache.lock_dir': './cache/lock'
}))   

_lookup = TemplateLookup(directories=['./templates'],
                          input_encoding='utf-8',
                          output_encoding='utf-8',
                          encoding_errors='replace',
                          module_directory="./tmp",
                          cache_impl='beaker',
                          cache_args={'manager':memary_manager } )  

pagesize = 30


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
    return render("error.html",error=msg)        

    
def auth_user(func):
    def warp(*args,**kwargs):
        session = web.ctx.session 
        if not session or not session.get("user"):
            raise web.seeother("/login",absolute=True)
        else:
            return func(*args,**kwargs)
    return warp


def filter_tags(htmlstr):
    """
    ##过滤HTML中的标签
    #将HTML中标签等信息去掉
    #@param htmlstr HTML字符串."""
    #先过滤CDATA
    re_cdata=re.compile('//<!\[CDATA\[[^>]*//\]\]>',re.I) #匹配CDATA
    re_script=re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>',re.I)#Script
    re_style=re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>',re.I)#style
    re_br=re.compile('<br\s*?/?>')#处理换行
    re_h=re.compile('</?\w+[^>]*>')#HTML标签
    re_comment=re.compile('<!--[^>]*-->')#HTML注释
    s=re_cdata.sub('',htmlstr)#去掉CDATA
    s=re_script.sub('',s) #去掉SCRIPT
    s=re_style.sub('',s)#去掉style
    s=re_br.sub('\n',s)#将br转换为换行
    s=re_h.sub('',s) #去掉HTML 标签
    s=re_comment.sub('',s)#去掉HTML注释
    #去掉多余的空行
    blank_line=re.compile('\n+')
    s=blank_line.sub('\n',s)
    s=replaceCharEntity(s)#替换实体
    return s


def replaceCharEntity(htmlstr):
    """
    ##替换常用HTML字符实体.
    #使用正常的字符替换HTML中特殊的字符实体.
    #你可以添加新的实体字符到CHAR_ENTITIES中,处理更多HTML字符实体.
    #@param htmlstr HTML字符串.
    """
    CHAR_ENTITIES={'nbsp':' ','160':' ',
                'lt':'<','60':'<',
                'gt':'>','62':'>',
                'amp':'&','38':'&',
                'quot':'"','34':'"',}
    
    re_charEntity=re.compile(r'&#?(?P<name>\w+);')
    sz=re_charEntity.search(htmlstr)
    while sz:
        entity=sz.group()#entity全称，如>
        key=sz.group('name')#去除&;后entity,如>为gt
        try:
            htmlstr=re_charEntity.sub(CHAR_ENTITIES[key],htmlstr,1)
            sz=re_charEntity.search(htmlstr)
        except KeyError:
            #以空串代替
            htmlstr=re_charEntity.sub('',htmlstr,1)
            sz=re_charEntity.search(htmlstr)
    return htmlstr



def filter_html(htmlstr):
    if not htmlstr:
        return htmlstr 
    htmlstr = htmlstr.replace("<","&lt;")
    htmlstr = htmlstr.replace(">","&gt;")
    return htmlstr


