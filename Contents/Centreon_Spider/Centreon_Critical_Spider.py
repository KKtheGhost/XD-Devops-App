#!/usr/bin/env python
#-*- coding: utf-8 -*-
#@Date    : 2018-11-06 16:43:06
#@Author  : Kivinsae Fang (fangwei@xindong.com)
#@QQ      : 1669815117
#@Version : 0.1.0

import urllib
import urllib2
import requests
import re
 
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11'}
 
## def get_xsrf():
##     firstURL = "https://jk002.xd.com/centreon/index.php"
##     request = urllib2.Request(firstURL,headers = headers)
##     response = urllib2.urlopen(request)
##     content = response.read()
##     pattern = re.compile(r'name="_xsrf" value="(.*?)"/>',re.S)
##     _xsrf = re.findall(pattern,content)
##     return _xsrf[0]
 
def login(par1):
    s = requests.session()
    afterURL = "https://assets.xd.com/index.php?page=object&object_id=889"        # 想要爬取的登录后的页面
    loginURL = "https://assets.xd.com/index.php?page=perms&tab=edit"     # POST发送到的网址
    login = s.post(loginURL, data = par1, headers = headers)                  # 发送登录信息，返回响应信息（包含cookie）
    response = s.get(afterURL, cookies = login.cookies, headers = headers)    # 获得登陆后的响应信息，使用之前的cookie
    return response.content
 
## xsrf = get_xsrf()
## print "_xsrf的值是：" + xsrf
data = {"username":"fangwei","password":"tF88K1CU1"}
## data = {"email":"fangwei","password":"tF88K1CU1","_xsrf":xsrf}
print login(data)
