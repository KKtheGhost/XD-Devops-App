#!/usr/bin/env python
#-*- coding: utf-8 -*-
#@Date    : 2018-11-06 16:43:06
#@Author  : Kivinsae Fang (fangwei@xindong.com)
#@QQ      : 1669815117
#@Version : 0.1.0

import paramiko
import time
import os
import sys
import datetime

reload(sys)
sys.setdefaultencoding('utf-8') 

##这个部分主要是创建临时记录文件，从而之后可以拿来对比。
def jk002SSH(ip,username,raw_cmd,i):
    reslist = open('/Users/kivinsaefang/Desktop/Devops-app/Contents/ArchiveCheck/reslist/'+str(i),'w')
    reslist.seek(0)
    reslist.truncate()
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.load_system_host_keys()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        pkey = paramiko.RSAKey.from_private_key_file('/Users/kivinsaefang/.ssh/id_rsa')         ##设定SSH免密登录
        ssh_client.connect(ip,22,username,pkey=pkey)
        date = datetime.date.today() - datetime.timedelta(days=1)	# 2015-10-29 00:00:00
        date_format = date.strftime('%Y/%m/%d')
        cmd = raw_cmd.replace('*date*',date_format)                                         ##设定ssh_client的登录信息
        stdin,stdout,stderr = ssh_client.exec_command(cmd,get_pty=True)                  ##运行需要的查询指令
        for line in stdout:
            print >> reslist,line.strip()
    except Exception,e:
        print e

##主执行函数
def S3read():
    cmdfile = open('/Users/kivinsaefang/Desktop/Devops-app/Contents/ArchiveCheck/ArchiveS3List','r')
    cmdline = cmdfile.readlines()
    ip,username = '172.26.0.65','root'              ##通过某一个有S3 read权限的号前往，服务器随意
    i = 0
    while i < len(cmdline):
        raw_cmd = cmdline[i].strip()
        jk002SSH(ip,username,raw_cmd,i)
        print 'Done!' + raw_cmd
        i += 1

## 具体执行
S3read()
