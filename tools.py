#coding:utf-8
import datetime
import re

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

def convtime(ctime):
    if not ctime:
        return ''
    cdate = datetime.datetime.strptime(ctime,'%Y-%m-%d %H:%M:%S')
    nowdate = datetime.datetime.now()
    dt = nowdate - cdate
    secs = dt.total_seconds() 

    if secs < 60:
        return u"刚刚"
    minute = int(secs/60)
    if minute >= 1 and minute < 60 :
        return u"%s分钟前"%minute

    hours = int(secs / (60*60))
    if hours >= 1 and hours < 24 :
        return u"%s小时前"%hours  

    days = int(secs / (60*60*24))
    if days >=1 and days<31:
        return u"%s天前"%days  

    months = int(secs / (60*60*24*30))
    if months >=1 and months<12:
        return u"%s月前"%months  

    years = int(secs / (60*60*24*365))
    return u"%s年前"%years  

if __name__ == "__main__":
    md = model(table="user",a=1,b=3)
    print dir(md.objects())
    print  md.objects()