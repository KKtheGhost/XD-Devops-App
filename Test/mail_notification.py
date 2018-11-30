#!/usr/bin/python
# -*- coding: UTF-8 -*-
 
import smtplib
from email.mime.text import MIMEText
from email.header import Header
 
sender = 'XD-Devapp—Daily@runoob.com'
receivers = ['fangwei@xindong.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
 
# 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
message = MIMEText('心动运维每日检查结果邮件测试', 'plain', 'utf-8')
message['From'] = Header("每日自动检测机", 'utf-8')   # 发送者
message['To'] =  Header("方苇", 'utf-8')        # 接收者
 
subject = '心动运维每日脚本测试'
message['Subject'] = Header(subject, 'utf-8')
 
 
try:
    smtpObj = smtplib.SMTP('localhost')
    smtpObj.sendmail(sender, receivers, message.as_string())
    print "邮件发送成功"
except smtplib.SMTPException:
    print "Error: 无法发送邮件"