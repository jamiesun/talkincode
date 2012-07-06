#!/usr/bin/python2.7 
#coding:utf-8
from settings import route_app,logger
import codestore
import json
import web

app  = route_app()

@app.route("/code/add")
class code_add():
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
    def GET(self,uid):
        try:
            content = codestore.get_content(uid)
            return json.dumps(content)
        except:
            return json.dumps({"error":"query data error"})  
