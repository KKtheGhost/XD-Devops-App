#!/usr/bin/env python
#-*- coding: utf-8 -*-
#@Date    : 2018-11-06 16:43:06
#@Author  : Kivinsae Fang (fangwei@xindong.com)
#@QQ      : 1669815117
#@Version : 0.1.0

import paramiko
import os
import math

def ssh2(ip,username,passwd,cmd):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip,22,username,passwd,timeout=5)
        stdin,stdout,stderr = ssh.exec_command("influx -username admin -password influxdb -database xd_callback -execute 'SELECT * FROM archive WHERE time>1541460282000000000'")
#           stdin.write("Y")   #简单交互，输入 ‘Y’
        print stdout.read()
        ssh.close()
    except :
        print '%stErrorn'%(ip)
ssh2("192.168.0.102","root","361way","hostname;ifconfig")
ssh2("192.168.0.107","root","123456","ifconfig")