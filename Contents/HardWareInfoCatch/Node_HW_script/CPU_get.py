#!/usr/bin/env python
#-*- coding: utf-8 -*-
#@Date    : 2018-11-06 16:43:06
#@Author  : Kivinsae Fang (fangwei@xindong.com)
#@QQ      : 1669815117
#@Version : 0.1.0

import os
import commands

def cpu_live_usage():           ##返回CPU_error,作为之后的判断。
    cpu_live_status_command = 'top -b -n 1|grep Cpu'
    cpu_live_status = commands.getoutput(cpu_live_status_command)
    if cpu_live_status == '':
        print '请安装top工具或者检查本机cpu状态'
        cpu_error = 'unknown'
        cpu_system_error = 'unknown'
        return cpu_error,cpu_system_error
    else:
        cpu_user_usage = (filter(lambda ch: ch in '0123456789. ', cpu_live_status)).split(  )[0]
        cpu_system_usage = (filter(lambda ch: ch in '0123456789. ', cpu_live_status)).split(  )[1]
        ## 用户进程占用量报警
        if int(cpu_user_usage) > 90:
            cpu_error = "critical"
        elif int(cpu_user_usage) >70:
            cpu_error = "warning"
        elif int(cpu_user_usage) >50:
            cpu_error = "high_usage"
        else:
            cpu_error = "health"
        ## 系统进程占用量报警
        if int(cpu_system_usage) > 90:
            cpu_system_error = "critical"
        elif int(cpu_system_usage) >70:
            cpu_system_error = "warning"
        elif int(cpu_system_usage) >50:
            cpu_system_error = "high_usage"
        else:
            cpu_system_error = "health"
        return cpu_error,cpu_system_error           ##获得了当前时刻的CPU主要占用状态

cpu_live_usage()