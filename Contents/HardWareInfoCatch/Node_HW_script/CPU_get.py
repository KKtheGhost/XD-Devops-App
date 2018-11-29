#!/usr/bin/env python
#-*- coding: utf-8 -*-
#@Date    : 2018-11-06 16:43:06
#@Author  : Kivinsae Fang (fangwei@xindong.com)
#@QQ      : 1669815117
#@Version : 0.1.0

from __future__ import division
import os
import commands

def cpu_live_usage():           ##返回CPU_error,作为之后的判断。
    cpu_live_status_command = 'top -b -n 1|grep Cpu|head -n 1'
    cpu_live_status = commands.getoutput(cpu_live_status_command)
    if cpu_live_status == '':
        print '请安装top工具或者检查本机cpu状态'
        cpu_error = 'unknown'
        cpu_usage_percent = 2
        return cpu_error,cpu_usage_percent
    else:
        cpu_user_usage = (filter(lambda ch: ch in '0123456789. ', cpu_live_status)).split(  )[0]
        cpu_system_usage = (filter(lambda ch: ch in '0123456789. ', cpu_live_status)).split(  )[1]
        ## 用户进程占用量报警
        if (float(cpu_user_usage) + float(cpu_system_usage)) > 90:
            cpu_error = "critical"
            cpu_usage_percent = (float(cpu_user_usage) + float(cpu_system_usage))
        elif (float(cpu_user_usage) + float(cpu_system_usage)) > 70:
            cpu_error = "warning"
            cpu_usage_percent = (float(cpu_user_usage) + float(cpu_system_usage))
        elif (float(cpu_user_usage) + float(cpu_system_usage)) > 50:
            cpu_error = "high_usage"
            cpu_usage_percent = (float(cpu_user_usage) + float(cpu_system_usage))
        else:
            cpu_error = "health"
            cpu_usage_percent = (float(cpu_user_usage) + float(cpu_system_usage))
        return cpu_error,cpu_usage_percent           ##获得了当前时刻的CPU状态和占用比例

cpu_live_usage()