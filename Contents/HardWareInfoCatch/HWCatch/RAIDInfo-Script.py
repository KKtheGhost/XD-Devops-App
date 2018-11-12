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
            ## if 'Error' in line:
            char = line        
            print >> stdoutfile,char   
       ssh_client.close()            
    except Exception,e:
       print e


GetRAID(ip,username,CliCheck)