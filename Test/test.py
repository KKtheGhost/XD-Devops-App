#!/usr/bin/env python
#-*- coding: utf-8 -*-
#@Date    : 2018-11-06 16:43:06
#@Author  : Kivinsae Fang (fangwei@xindong.com)
#@QQ      : 1669815117
#@Version : 0.3.0

import os
import commands

def basebasei(self):
    if x == 0:
        return 0
    else:
        return 2 * basebasei(x - 1) + x * x

basebasei(1)
