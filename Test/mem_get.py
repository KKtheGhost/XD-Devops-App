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
    mem_live_status_command = 'free -m|head -n 2|sed 1d'
    mem_live_status = commands.getoutput(mem_live_status_command)
    if mem_live_status == '': 
        print '请安装top工具或者检查本机cpu状态'
        mem_error = 'unknown'
        mem_usage_percent = 'unknown'
    else:
        mem_total = int((filter(lambda ch: ch in '0123456789. ', mem_live_status)).split(  )[0])
        mem_available = int((filter(lambda ch: ch in '0123456789. ', mem_live_status)).split(  )[-1])
        mem_usage = mem_total - mem_available
        mem_usage_percent = ('%.5f' %(mem_usage/mem_total))
	mem_100_usage = float(mem_usage_percent) * 100	
	if mem_100_usage > 50:
	    if mem_100_usage > 70:
		if mem_100_usage > 95:
		    mem_error = 'critical'
		else:
		    mem_error = 'warning'
	    else:
		mem_error = 'medium'
	else:
            mem_error = 'healthy'
        return mem_error,mem_100_usage           ##获取了实时的内存状态和占用比例:wq

print '当前内存使用量状态为: ' + mem_live_usage()[0]
print '具体占用量: ' + str(mem_live_usage()[1]) + '%'