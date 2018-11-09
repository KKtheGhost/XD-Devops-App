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

timespit = str(1000000000 * int(time.mktime(time.strptime(str(datetime.date.today()), '%Y-%m-%d'))))

jk002ip,jk002username = '10.1.52.1','root'

cmdline = 0
sshcommand = ''

## def INFCommand(cmd):
##     cmdfile = open('./jk002INFCMD','r')
##     projcmd = cmdfile.readlines()[cmdline]
##     for i in projcmd.strip():
##         cmd += i

def jk002SSH(ip,username,cmd,stdoutfile):
    ## callbackLogFile = open("./CallBack_daily_log","a")
    ## callbackLogFile.seek(0)
    ## callbackLogFile.truncate()
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.load_system_host_keys()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        pkey = paramiko.RSAKey.from_private_key_file('/Users/kivinsaefang/.ssh/id_rsa')         ##设定SSH免密登录
        ssh_client.connect(ip,22,username,pkey=pkey)                                            ##设定ssh_client的登录信息
        stdin,stdout,stderr = ssh_client.exec_command(cmd,get_pty=True)                  ##运行需要的查询指令
        ##在command命令最后加上 get_pty=True，执行多条命令 的话用；隔开，另外所有命令都在一个大的单引号范围内引用
        ##std_in.write('PWD'+'\n') #执行输入命令，输入sudo命令的密码，会自动执行
        ##stdout.encode('gb2312')
        for line in stdout:
            line = line.strip() ##删除换行符，防止出现空行
            char = line         ##变量分离
            print >> stdoutfile,char       ##输出到文件："./CallBack_daily_log"
            ## callbackLogFile.write(stdout.read())
        ssh_client.close()                      ##完成操作，关闭ssh_client
    except Exception,e:
        print e

def CallbackOut(num,cmd,ip,username,rplcment):    
    callbackLogFile = open("./CallBack_BackupDailyLog","a")
    callbackLogFile.seek(0)
    callbackLogFile.truncate()
    while num < 15:
        cmdfile = open('./jk002_BackupCmd','r')
        projcmd = cmdfile.readlines()[num]
        projcmd = projcmd.replace('timespit',rplcment)
        for i in projcmd.strip():
            cmd += i
        print cmd
        jk002SSH(ip,username,cmd,callbackLogFile)
        num += 1
        cmd = ''
        print 'Stdout OK!'
    print 'Done!'

CallbackOut(cmdline,sshcommand,jk002ip,jk002username,timespit)