#!/usr/bin/env python
#-*- coding: utf-8 -*-
#@Date    : 2018-11-06 16:43:06
#@Author  : Kivinsae Fang (fangwei@xindong.com)
#@QQ      : 1669815117
#@Version : 0.1.0

import paramiko
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

CliCheck = '/opt/MegaRAID/MegaCli/MegaCli64 -PDList -A0|grep -iE \'slot|error|Non Coerced\''
ip,username = '10.1.54.185','root'

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
            if 'Error' in line:
                char = line        
                print >> stdoutfile,char   
       ssh_client.close()            
    except Exception,e:             ##需要添加相关的信息筛选策略，明天的目标
       print e

def ErrorGet(project):
    openfile = open("./Temporary_RAID_INFO","r")
    errorout = open("./ErrorRaidDaily","a")
    errorout.seek(0)
    errorout.truncate()
    if len(openfile.readlines()) < 12:
        print project
    linenum = 0
    while linenum < (len(openfile.readlines())):
        elineslot = openfile.readline()[linenum]
        eline1 = openfile.readline()[linenum+1]
        eline2 = openfile.readline()[linenum+2]
        elinesize = openfile.readline()[linenum+3]
        if eline1[19:20] == '0' and eline2[19:20] == '0':
            continue
        else:
            print elineslot + elinesize >> ''
        linenum += 4

count = 1
def GetServerInfo(count):
    hostfile = open("./ServerHost.conf","r")
    ip = hostfile.readline()[count * 4]
    username = hostfile.readline()[count * 4 + 1]
    project = hostfile.readline()[count * 4 + 2]




    
GetRAID(ip,username,CliCheck)