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
from datetime import timedelta, datetime

reload(sys)
sys.setdefaultencoding('utf-8') 
cmdfile = open('/Users/kivinsaefang/Desktop/Devops-app/Contents/ArchiveCheck/ArchiveS3List','r')
cmdline = cmdfile.readlines()
ip,username = '172.26.0.65','root'              ##通过某一个有S3 read权限的号前往，服务器随意
## 本函数获得单个项目的归档字段，输出部分为一个临时文本文件。循环组件
def jk002SSH(ip,username,cmd):                  ##需要外部输入的有：ip,username
    output = []
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.load_system_host_keys()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        pkey = paramiko.RSAKey.from_private_key_file('/Users/kivinsaefang/.ssh/id_rsa')         ##设定SSH免密登录
        ssh_client.connect(ip,22,username,pkey=pkey)                                            ##设定ssh_client的登录信息
        stdin,stdout,stderr = ssh_client.exec_command(cmd,get_pty=True)                  ##运行需要的查询指令
        for line in stdout:
            print line
    except Exception,e:
        print e

date = datetime.today()
date_format = date.strftime('%Y/%m/%d')
rds = open('/Users/kivinsaefang/Desktop/Devops-app/Contents/ArchiveCheck/ArchiveRDSList','r')
for line in cmdline:
    i = 0
    raw_cmd = line[17:]
    cmd = raw_cmd.replace('*date*',date_format)
    rds_list = [str(x) for x in rds.split(',')]
    if rds_list == []:
        jk002SSH(ip,username,cmd)
    else:
        for rds in rds_list:
            cmd = cmd.replace('*rdsname*',rds)
            jk002SSH(ip,username,cmd)