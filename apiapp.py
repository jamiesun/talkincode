#!/usr/bin/python2.7 
#coding:utf-8
from settings import route_app,logger
import codestore
from store import get_conn
import json
import web

PUBLIC_KEY = '494ec9f9cbaf40cfa8d4b44447374d27'

def doauthkey(func):
    def func_warp(*args,**argkv):
        authkey = web.input().get("authkey")
        if not authkey:
            authkey=PUBLIC_KEY
        if type(authkey) == unicode:
            authkey = str(authkey)            
        conn = get_conn()
        cur = conn.cursor()
        try:
            cur.execute("select authkey,hits from authkeys where authkey=%s",(authkey))
            keyobjs = cur.fetchone()
            if not keyobjs:
                raise Exception('authkey not exists')
            authkey_hits = keyobjs[0][1]
            hits = int(authkey_hits) + 1
            cur.execute("update authkeys set hits = %s where authkey=%s",(hits,authkey))
            conn.commit()
            return func(*args,**argkv)
        finally:
            cur.close()
            conn.close()
    return func_warp    

app  = route_app()

@app.route("/code/add")
class code_add():
    @doauthkey
    def POST(self):
        forms = web.input()
        params = dict(pid=forms.get("pid"),
                      title = forms.get("title"),
                      auther = forms.get("auther"),
                      email = forms.get("email"),
                      tags = forms.get("tagstr"),
                      content = forms.get("content"),
                      authkey = forms.get("authkey"),
                      filename = forms.get("filename"),
                      lang=forms.get("lang"))
        try:
            codestore.add_code(**params)
            return "ok"
        except:
            return "error"

@app.route("/code/index")
class code_index():
    @doauthkey
    def GET(self):
        keyword = web.input().get("q") or ''
        limit = web.input().get("limit") or 1000

        try:
            tops = codestore.list_index(keyword=keyword,limit=limit) 
            return json.dumps(tops)
        except Exception,e:
            logger.error("query data error %s"%e)
            return json.dumps({"error":"query data error "})         

@app.route("/code/get/(.*)")
class code_get():
    @doauthkey
    def GET(self,uid):
        try:
            content = codestore.get_content(uid)
            return json.dumps(content)
        except:
            return json.dumps({"error":"query data error"})  
