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
import commands

reload(sys)
sys.setdefaultencoding('utf-8')

## 判断本机的aws是否可用。
def aws_valid_test():
    get_aws_certification_command = 'cat ~/.aws/credentials'
    aws_certification = commands.getoutput(get_aws_certification_command)
    ## 分两种情况，一个是用户机器已安装awscli，一种是没有安装awscli
    length = len(aws_certification.split('\n'))
    if length == 1:
        if aws_certification.split( )[0] == 'cat:' or aws_certification.split( )[0] == '-cat:':
            aws_certification_len = 0
        else:
            aws_certification_len = 1
    if length >=3:
        aws_certification_len = length
    else:
        return 0
    return aws_certification_len

## 主要功能部分:

##==============================================
## 当使用者机器有aws权限时，直接登录获取信息
def local_aws_get(ip,username,raw_cmd,i):
    reslist = open('/Users/kivinsaefang/Desktop/Devops-app/Contents/ArchiveCheck/reslist/'+str(i),'w')
    reslist.seek(0)
    reslist.truncate()
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.load_system_host_keys()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        pkey = paramiko.RSAKey.from_private_key_file('/Users/kivinsaefang/.ssh/id_rsa')         ##设定SSH免密登录
        ssh_client.connect(ip,22,username,pkey=pkey)
        date = datetime.date.today() - datetime.timedelta(days=1)	# 2015-10-29 00:00:00
        date_format = date.strftime('%Y/%m/%d')
        cmd = raw_cmd.replace('*date*',date_format)                                         ##设定ssh_client的登录信息
        stdin,stdout,stderr = ssh_client.exec_command(cmd,get_pty=True)                  ##运行需要的查询指令
        for line in stdout:
            print >> reslist,line.strip()
    except Exception,e:
        print e

## 本地执行主程序
def S3read_local():
    cmdfile = open('/Users/kivinsaefang/Desktop/Devops-app/Contents/ArchiveCheck/ArchiveS3List','r')
    cmdline = cmdfile.readlines()
    ip,username = '172.26.0.65','root'              ##通过某一个有S3 read权限的号前往，服务器随意
    i = 0
    while i < len(cmdline):
        raw_cmd = (cmdline[i].strip())[16:]
        cmdfile.close()
        local_aws_get(ip,username,raw_cmd,i)
        out_reslist = open('/Users/kivinsaefang/Desktop/Devops-app/Contents/ArchiveCheck/reslist/'+str(i),'r')
        num_reslist = len(out_reslist.readlines())
        out_reslist_std = open('/Users/kivinsaefang/Desktop/Devops-app/Contents/ArchiveCheck/reslist_std/'+str(i),'r')
        num_reslist_std = len(out_reslist_std.readlines())
        if num_reslist == num_reslist_std:
            archive_res = 'Yes! ' + (cmdline[i].strip())[:15] + ' was successfully archived.'
            print archive_res
        if num_reslist > num_reslist_std:
            archive_res = 'Yes! ' + (cmdline[i].strip())[:15] + ' was successfully archived.'
            os.system('cp /Users/kivinsaefang/Desktop/Devops-app/Contents/ArchiveCheck/reslist/' + str(i) + ' /Users/kivinsaefang/Desktop/Devops-app/Contents/ArchiveCheck/reslist_std/' + str(i))
            print archive_res
        if num_reslist < num_reslist_std:
            archive_res = 'Oops! There are(is) ' + str(num_reslist_std - num_reslist) + ' error(s) of ' + (cmdline[i].strip())[:15] + ' were found during achiving.'
            print archive_res
            proj_head = (cmdline[i].strip())[:9]
            if proj_head == '香肠派' or proj_head == '最终王' or proj_head == '心灵战' or proj_head == '横冲直' or proj_head == '仙侠道' or proj_head == '香肠派':
                print '对应服务器是42x001.xd.cn'
            elif proj_head == '仙境传':
                print '对应服务器是51x001.xd.cn'
            elif proj_head == '神仙道':
                print '对应服务器是42x004.xd.cn'
            elif proj_head == '横扫千':
                print '对应服务器是46x003.xd.cn'
            else:
                print '对应管理服务器请手动查询'        
        i += 1

##===============================================
##当使用者机器没有aws权限时，通过paramiko插件走ssh跳板机
def remote_aws_acc_get(ip,username,raw_cmd,i):
    reslist = open('/Users/kivinsaefang/Desktop/Devops-app/Contents/ArchiveCheck/reslist/'+str(i),'w')
    reslist.seek(0)
    reslist.truncate()
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.load_system_host_keys()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        pkey = paramiko.RSAKey.from_private_key_file('/Users/kivinsaefang/.ssh/id_rsa')         ##设定SSH免密登录
        ssh_client.connect(ip,22,username,pkey=pkey)
        date = datetime.date.today() - datetime.timedelta(days=1)	# 2015-10-29 00:00:00
        date_format = date.strftime('%Y/%m/%d')
        cmd = raw_cmd.replace('*date*',date_format)                                         ##设定ssh_client的登录信息
        stdin,stdout,stderr = ssh_client.exec_command(cmd,get_pty=True)                  ##运行需要的查询指令
        for line in stdout:
            print >> reslist,line.strip()
    except Exception,e:
        print e

## devapp跳板主执行函数
def S3read_remote():
    cmdfile = open('/Users/kivinsaefang/Desktop/Devops-app/Contents/ArchiveCheck/ArchiveS3List','r')
    cmdline = cmdfile.readlines()
    ip,username = '172.26.0.65','root'              ##通过某一个有S3 read权限的号前往，服务器随意
    i = 0
    while i < len(cmdline):
        raw_cmd = (cmdline[i].strip())[16:]
        cmdfile.close()
        remote_aws_acc_get(ip,username,raw_cmd,i)
        out_reslist = open('/Users/kivinsaefang/Desktop/Devops-app/Contents/ArchiveCheck/reslist/'+str(i),'r')
        num_reslist = len(out_reslist.readlines())
        out_reslist_std = open('/Users/kivinsaefang/Desktop/Devops-app/Contents/ArchiveCheck/reslist_std/'+str(i),'r')
        num_reslist_std = len(out_reslist_std.readlines())
        if num_reslist == num_reslist_std:
            archive_res = 'Congratulation! ' + (cmdline[i].strip())[:15] + ' has successfully archived.'
            print archive_res
        if num_reslist > num_reslist_std:
            archive_res = 'Congratulation! ' + (cmdline[i].strip())[:15] + ' has successfully archived.'
            os.system('cp /Users/kivinsaefang/Desktop/Devops-app/Contents/ArchiveCheck/reslist/' + str(i) + ' /Users/kivinsaefang/Desktop/Devops-app/Contents/ArchiveCheck/reslist_std/' + str(i))
            print archive_res
        if num_reslist < num_reslist_std:
            archive_res = 'Oops! There are(is) ' + str(num_reslist_std - num_reslist) + ' error(s) of ' + (cmdline[i].strip())[:15] + ' were found during achiving.'
            print archive_res
            proj_head = (cmdline[i].strip())[:9]
            if proj_head == '香肠派' or proj_head == '最终王' or proj_head == '心灵战' or proj_head == '横冲直' or proj_head == '仙侠道' or proj_head == '香肠派':
                print '对应服务器是42x001.xd.cn'
            elif proj_head == '仙境传':
                print '对应服务器是51x001.xd.cn'
            elif proj_head == '神仙道':
                print '对应服务器是42x004.xd.cn'
            elif proj_head == '横扫千':
                print '对应服务器是46x003.xd.cn'
            else:
                print '对应管理服务器请手动查询'        
        i += 1

##==============##==============##==============##==============##
## 具体执行
def s3_checkout():
    if aws_valid_test() >= 3:       ##本地安装AWS cli且有certificate
        region_get_command = 'cat ~/.aws/config|grep region|awk \'{print $3}\''
        aws_region = commands.getoutput(region_get_command)
        if aws_region == 'cn-north-1':
            S3read_local()
        else:
            no_region_choice = raw_input('请设置一个有效的AWS区域，详细配置请参考AWS官方文档。如果需要调用远程代理查看，请输入y。若需要退出请输入n:')
            if no_region_choice == 'y' or no_region_choice == 'Y':
                S3read_remote()
            else:
                return 0
    elif aws_valid_test() == 1:     ##本地安装AWS cli，但是没有certificate
        print '没有检测到AWS证书.'
        key_input = raw_input('是否需要输入AccessKey?(y/n):')
        if key_input == 'y' or key_input == 'Y':                ## 主要需要设置 keyID AccessKey output region
            aws_access_key_id = raw_input('请输入aws_access_key_id:')
            aws_secret_access_key = raw_input('请输入aws_secret_access_key:')
            aws_output = 'output = jsonjson'
            aws_region = 'region = cn-north-1'
            aws_common_config = open('~/.aws/config','a')
            print >> aws_common_config,aws_output
            print >> aws_common_config,aws_region
            aws_credential_config = open('~/.aws/credentials','a')
            print >> aws_credential_config,aws_access_key_id
            print >> aws_credential_config,aws_secret_access_key
            S3read_local()
        else:
            no_certificate_choice = raw_input('无有效certificate，抱歉。如果需要调用远程代理查看，请输入y。若需要退出请输入n:')
            if no_certificate_choice == 'y' or no_certificate_choice == 'Y':
                S3read_remote()
            else:
                return 0
    elif aws_valid_test() == 0:     ##本地压根没有装AWS，直接remote检测
        print '本机未安装AWS cli软体或者依赖，为您跳转到远程跳板进行S3检测'
        S3read_remote()
    else:
        print "Error!"
        return 0
    
## 主程序Bingo！
s3_checkout()
