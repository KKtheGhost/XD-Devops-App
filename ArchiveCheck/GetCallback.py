#!/usr/bin/env python
#-*- coding: utf-8 -*-
#@Date    : 2018-11-06 16:43:06
#@Author  : Kivinsae Fang (fangwei@xindong.com)
#@QQ      : 1669815117
#@Version : 0.1.0

import paramiko
import os
import math

#var definition
def sshlogin(ip,username,pkey):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip,22,username,pkey,timeout=5)
    except :
        print '%stErrorn'%(ip)

def sshlogout()
	ssh.close()

def callback()
	stdin, stdout, stderr = ssh.exec_command("influx -username admin -password influxdb -database xd_callback -execute 'select * from archive where project=ro'")
	print stdout.readlines(./TodayCallback.txt)
sshlogin("10.1.52.1",22,"root",)
callback()

