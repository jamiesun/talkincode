#!/usr/bin/python2.7 
#coding:utf-8
from settings import route_app,filter_html,render,logger
from settings import errorpage,auth_user
import groupstore
import web

app  = route_app()

@app.route("")
class routeto():
    def GET(self):
        raise web.seeother("/group/",absolute=True)

@app.route("/")
class index():
    def GET(self):
        groups = groupstore.list_groups()
        stats = groupstore.get_post_stats()
        tops = groupstore.list_posts()
        return render("group.html",
            tops = tops,
            groups=groups,
            stats=stats,
            get_user=groupstore.get_user,
            get_group=groupstore.get_group) 

@app.route("/category/(.*)")
class index():
    def GET(self,guid):
        groups = groupstore.list_groups()
        stats = groupstore.get_post_stats(guid)
        tops = groupstore.list_posts_by_guid(guid)
        return render("group.html",
            tops = tops,
            groups=groups,
            stats=stats,
            get_user=groupstore.get_user,
            get_group=groupstore.get_group) 

@app.route("/post/add")
class add_post():
    @auth_user
    def GET(self):
        groups = groupstore.list_groups()
        return render("post_add.html",groups=groups) 

    @auth_user
    def POST(self):
        user = web.ctx.session.get("user")
        form = web.input()
        title = form.get("title")
        tags = form.get("tags")
        gid = form.get("gid")
        content = form.get("content")
        userid = user["id"]
        if not title or not gid or not content:
            return errorpage(u"请输入完整数据")
        try:
            groupstore.add_post(gid,userid,title,tags,content)
            raise web.seeother("/group/",absolute=True)
        except Exception, e:
            return errorpage("add post error %s"%e)


@app.route("/post/update")
class update_post():
    @auth_user
    def GET(self):
        pass

@app.route("/post/get")
class get_post():
    @auth_user
    def GET(self):
        pass        