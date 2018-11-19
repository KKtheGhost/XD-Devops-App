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

## 参数获得
ip,username = '10.1.52.1','root'

## 本函数获得单个项目的归档字段，输出部分为一个临时文本文件。循环组件
def jk002SSH(ip,username,cmd):       ##需要外部输入的有：ip,username
    outfile = open('/Users/kivinsaefang/Desktop/Devops-app/Contents/ArchiveCheck/CallBack_ArchiveDailyLog','a')
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.load_system_host_keys()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        pkey = paramiko.RSAKey.from_private_key_file('/Users/kivinsaefang/.ssh/id_rsa')         ##设定SSH免密登录
        ssh_client.connect(ip,22,username,pkey=pkey)                                            ##设定ssh_client的登录信息
        stdin,stdout,stderr = ssh_client.exec_command(cmd,get_pty=True)                  ##运行需要的查询指令
        for line in stdout:
            line = line.strip() ##删除换行符，防止出现空行
            if 'archive' in line:
                continue
            elif 'time' in line:
                continue
            elif '----' in line:
                continue
            else:
                char = line[20:]
                print >> outfile,char 
        ssh_client.close()
    except Exception,e:
        print e

## 本函数用来将项目归档字段和标准归档字段进行比较。并且输出比较结果。循环组件
def ArchCompare(proj):
    log = open('/Users/kivinsaefang/Desktop/Devops-app/Contents/ArchiveCheck/CallBack_ArchiveDailyLog','r')
    loglines = log.readlines()         ## 当前项目的列表，列表A
    std = open('/Users/kivinsaefang/Desktop/Devops-app/Contents/ArchiveCheck/STD_ArchiveLog','r')
    stdlines = std.readlines()
    stdproj = []
    for stdline in stdlines:
        if proj == (stdline[7:12]).strip():
            stdproj += stdline              ## 列表B，标准列表
    retA = list(set(stdproj).difference(set(loglines)))
    print "Differences are: ",retA


## 本函数获得cmd命令
def docmd(x):
    cmdfile = open('/Users/kivinsaefang/Desktop/Devops-app/Contents/ArchiveCheck/jk002_ArchiveCmd','r')
    cmds = cmdfile.readlines()          ## 一个CMD集合的列表
    cmd = cmds[x]

## 本函数用来整理，剪切，整合输出比较结果（循环）
def finaloutput():
    global ip,username
    cmdfile = open('/Users/kivinsaefang/Desktop/Devops-app/Contents/ArchiveCheck/jk002_ArchiveCmd','r')
    cmds = cmdfile.readlines()
    x = 0
    while x <= 13:
        cmd = cmds[x]
        project = open('/Users/kivinsaefang/Desktop/Devops-app/Contents/ProjList','r')
        projs = project.readlines()
        proj = projs[x]
        jk002SSH(ip,username,cmd)
        ArchCompare(proj)
        x += 1

finaloutput()


