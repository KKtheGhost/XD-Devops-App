#!/usr/bin/env python
#-*- coding: utf-8 -*-
#@Date    : 2018-11-06 16:43:06
#@Author  : Kivinsae Fang (fangwei@xindong.com)
#@QQ      : 1669815117
#@Version : 0.1.0

from __future__ import division
import os
import commands

def mem_live_usage():           ##返回CPU_error,作为之后的判断。
    mem_live_status_command = 'free -wm|head -n 2|sed 1d'
    mem_live_status = commands.getoutput(mem_live_status_command)
    if mem_live_status == '': 
        print '请安装top工具或者检查本机cpu状态'
        mem_error = 'unknown'
        mem_usage_percent = 'unknown'
        return mem_error,mem_usage_percent
    elif mem_live_status.split( )[0] == 'free:':
        mem_live_status_command = 'free -m|head -n 2|sed 1d'
        mem_live_status = commands.getoutput(mem_live_status_command)
        mem_total = (filter(lambda ch: ch in '0123456789. ', mem_live_status)).split(  )[0]
        mem_available = (filter(lambda ch: ch in '0123456789. ', mem_live_status)).split(  )[-1]
        mem_usage = int(mem_total) - int(mem_available)
        mem_usage_percent = ('%.1f' %(100*mem_usage/int(mem_total)))
        if mem_usage_percent > 0.5:
            mem_error = 'medium'
        elif mem_usage_percent > 0.7:
            mem_error = 'warning'    
        elif mem_usage_percent > 0.95:
            mem_error = 'critical'
        else:
            mem_error = 'healthy'
        return mem_error,mem_usage_percent           ##获取了实时的内存状态和占用比例:wq
    else:
        mem_total = (filter(lambda ch: ch in '0123456789. ', mem_live_status)).split(  )[0]
        mem_available = (filter(lambda ch: ch in '0123456789. ', mem_live_status)).split(  )[-1]
        mem_usage = int(mem_total) - int(mem_available)
        mem_usage_percent = ('%.1f' %(100*mem_usage/int(mem_total)))
        if mem_usage_percent > 0.5:
            mem_error = 'medium'
        elif mem_usage_percent > 0.7:
            mem_error = 'warning'    
        elif mem_usage_percent > 0.95:
            mem_error = 'critical'
        else:
            mem_error = 'healthy'
        return mem_error,mem_usage_percent           ##获取了实时的内存状态和占用比例:wq

mem_live_usage()