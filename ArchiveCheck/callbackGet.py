#!/usr/bin/env python
#-*- coding: utf-8 -*-
#@Date    : 2018-11-06 16:43:06
#@Author  : Kivinsae Fang (fangwei@xindong.com)
#@QQ      : 1669815117
#@Version : 0.1.0

import paramiko
import time
import datetime

t = time.localtime(time.time())
timespit = str(1000000000 * int(time.mktime(time.strptime(time.strftime('%Y-%m-%d 00:00:00', t),'%Y-%m-%d %H:%M:%S'))))

ip,username = '10.1.52.1','root'
influxCommand = str('influx -username admin -password influxdb -database xd_callback -execute \'select * from archive where time>'+timespit+"\';")
##def ssh2(ip,username,passwd,cmd):
try:
    ssh_client = paramiko.SSHClient()
    ssh_client.load_system_host_keys()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    pkey = paramiko.RSAKey.from_private_key_file('/Users/kivinsaefang/.ssh/id_rsa')
    ssh_client.connect(ip,22,username,pkey=pkey)
    std_in,std_out,std_err = ssh_client.exec_command(influxCommand,get_pty=True)  
    #在command命令最后加上 get_pty=True，执行多条命令 的话用；隔开，另外所有命令都在一个大的单引号范围内引用
    ##std_in.write('PWD'+'\n') #执行输入命令，输入sudo命令的密码，会自动执行
    for line in std_out:
        print line.strip('\n')
    ssh_client.close()
except Exception,e:
    print e