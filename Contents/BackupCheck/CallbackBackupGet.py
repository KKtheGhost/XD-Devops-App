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

def jk002SSH(ip,username,cmd,stdoutfile):
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.load_system_host_keys()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        pkey = paramiko.RSAKey.from_private_key_file('/Users/kivinsaefang/.ssh/id_rsa')         ##设定SSH免密登录
        ssh_client.connect(ip,22,username,pkey=pkey)                                            ##设定ssh_client的登录信息
        stdin,stdout,stderr = ssh_client.exec_command(cmd,get_pty=True)                  ##运行需要的查询指令
        for line in stdout:
            line = line.strip() 
            if 'backup' in line:
                continue
            elif 'time' in line:
                continue
            elif '----' in line:
                continue
            else:
                char = line[20:]        
                print >> stdoutfile,char   
        ssh_client.close()            
    except Exception,e:
        print e

def CompareError(project):
    BackupStatus = 0
    TodayLog = open("/Users/kivinsaefang/Desktop/Devops-app/Contents/BackupCheck/CallBack_BackupDailyLog","r")
    StandardLog = open("/Users/kivinsaefang/Desktop/Devops-app/Contents/BackupCheck/STD_BackupLog","r")
    TodayLogLines = TodayLog.readlines()
    StandardLogLines = StandardLog.readlines()
    StandardLogProj,ErrorLine = [],[]
    for stdline in StandardLogLines:             ##不可优化部分，STDBackupsout存在随业务变化的可能。
        StandardLogProj += stdline
    for line in TodayLogLines:
        if line.strip() not in StandardLogProj:
            ErrorLine += line.strip()[15:((line.strip()[15:]).append(' '))]     ##通过append获取rdsname
            BackupStatus += 1
    if BackupStatus == 0:
        print project + '\'s backup is perfect today.'
    else:
        print 'There is ' + str(BackupStatus) + ' errors of ' + project + ' in Backup today. The error RDSserver is ' + ErrorLine 

def CallbackOut(num,cmd,ip,username):
    timespit = str(1000000000 * int(time.mktime(time.strptime(str(datetime.date.today()), '%Y-%m-%d'))))     
    callbackLogFile = open("/Users/kivinsaefang/Desktop/Devops-app/Contents/BackupCheck/CallBack_BackupDailyLog","a")
    callbackLogFile.seek(0)
    callbackLogFile.truncate()
    while num < 14:
        cmdfile = open('/Users/kivinsaefang/Desktop/Devops-app/Contents/BackupCheck/jk002_BackupCmd','r')
        projcmd = cmdfile.readlines()[num]
        projcmd = projcmd.replace('timespit',timespit)
        for i in projcmd.strip():
            cmd += i
        jk002SSH(ip,username,cmd,callbackLogFile)
        project = ((open('/Users/kivinsaefang/Desktop/Devops-app/Contents/ProjList','r').readlines()[num]).strip())[10:]
        num += 1
        cmd = ''
        CompareError(project)
    print 'Done!'

jk002ip,jk002username = '10.1.52.1','root'
cmdline = 0
sshcommand = ''

CallbackOut(cmdline,sshcommand,jk002ip,jk002username)