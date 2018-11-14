#!/usr/bin/env python
#-*- coding: utf-8 -*-
#@Date    : 2018-11-06 16:43:06
#@Author  : Kivinsae Fang (fangwei@xindong.com)
#@QQ      : 1669815117
#@Version : 0.1.0

import os

def checkBackupArchive():
    os.system('python ./Contents/BackupCheck/CallbackBackupGet.py')
    os.system('python ./Contents/ArchiveCheck/CallbackArchiveGet.py')

checkBackupArchive()