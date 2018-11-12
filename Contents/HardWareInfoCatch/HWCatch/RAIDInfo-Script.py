#!/usr/bin/env python
#-*- coding: utf-8 -*-
#@Date    : 2018-11-06 16:43:06
#@Author  : Kivinsae Fang (fangwei@xindong.com)
#@QQ      : 1669815117
#@Version : 0.1.0

import paramiko
import metrics
import sys
import commands

reload(sys)
sys.setdefaultencoding('utf-8')

def UploadHWInfo():
