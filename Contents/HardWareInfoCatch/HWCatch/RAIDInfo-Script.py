#!/usr/bin/env python
#-*- coding: utf-8 -*-
#@Date    : 2018-11-06 16:43:06
#@Author  : Kivinsae Fang (fangwei@xindong.com)
#@QQ      : 1669815117
#@Version : 0.1.0

import paramiko
# import sys
import linecache
import os

## reload(sys)
## sys.setdefaultencoding('utf-8')

CliCheck = '/opt/MegaRAID/MegaCli/MegaCli64 -PDList -A0|grep -iE \'slot|error|Non Coerced\''

def GetRAID(ip,username,cmd):
    stdoutfile = open("./Temporary_RAID_INFO","a")
    stdoutfile.seek(0)
    stdoutfile.truncate()
    try:
       ssh_client = paramiko.SSHClient()
       ssh_client.load_system_host_keys()
       ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
       pkey = paramiko.RSAKey.from_private_key_file('/Users/kivinsaefang/.ssh/id_rsa')
       ssh_client.connect(ip,22,username,pkey=pkey)
       stdin,stdout,stderr = ssh_client.exec_command(cmd,get_pty=True)
       for line in stdout:
            line = line.strip()
            ## if 'Error' in line:
            char = line        
            print >> stdoutfile,char   
       ssh_client.close()            
    except Exception,e:             ##需要添加相关的信息筛选策略，明天的目标
       print e

def ErrorGet(project):
    openfile,errorout = open("./Temporary_RAID_INFO","r"),open("./ErrorRaidDaily","a")
    errorout.seek(0)
    errorout.truncate()
    if len(openfile.readlines()) < 12:
        print project
    linenum = 0
    while linenum < (len(openfile.readlines())):
        elineslot,eline1,eline2,elinesize = openfile.readline()[linenum],openfile.readline()[linenum+1],openfile.readline()[linenum+2],openfile.readline()[linenum+3]
        if eline1[19:20] == '0' and eline2[19:20] == '0':
            continue
        else:
            print elineslot + elinesize >> errorout
        linenum += 4

count = 1
def GetServerInfo(num):
    hostfile = open("./ServerHost","rU")
    ipnum,usernum,projnum = num*4,num*4+1,num*4+2
    while num*4 < (len(hostfile.readlines())):
        ip = ((linecache.getline("./ServerHost",ipnum))[10:]).strip()
        username = ((linecache.getline("./ServerHost",usernum))[10:]).strip()
        project = ((linecache.getline("./ServerHost",projnum))[10:]).strip()
        GetRAID(ip,username,CliCheck)
        ErrorGet(project)

GetServerInfo(count)