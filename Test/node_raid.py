#!/usr/bin/env python
#-*- coding: utf-8 -*-
#@Date    : 2018-11-06 16:43:06
#@Author  : Kivinsae Fang (fangwei@xindong.com)
#@QQ      : 1669815117
#@Version : 0.1.0

import os
import commands

## 通用化：获取服务器raid卡和物理磁盘状态信息。return一个字典来判定是否输出到influxdb，具体输出内容存到本地临时文件进行推送。（暂时计划）
def get_server_raid_card_metrics():
    ## 判断服务器的供应商
    manufactory_check_command = 'dmidecode -t 1 | grep Manufacturer'
    manufactory = commands.getoutput(manufactory_check_command)
    ## 创建字典，作为是否导入数据库的判定。
    influx_raid_record_fields = {"raid_health": 1,"nvme_health":1,"physical_disk_health":1}
##========================================================================================
    ## 当server是dell的时候,不同型号的戴尔服务器存在不同的策略
    if (manufactory.split( ))[1] == 'Dell':
        dell_product_check_command = 'dmidecode -t 1 | grep Product'
        dell_product = commands.getoutput(dell_product_check_command)
        ## 当型号是R720或R620的时候==========================================
        if (dell_product.split( ))[3] == 'R720' or (dell_product.split( ))[3] == 'R620':
            ## "raid_health"对于阵列卡状态的判断
            raid_health_get_command = '/opt/MegaRAID/MegaCli/MegaCli64 -AdpAllInfo -aALL|grep -iE Virtual|awk \'{print $4}\''
            raid_health_info = commands.getoutput(raid_health_get_command)
            if raid_health_info == '': 
                influx_raid_record_fields["raid_health"] = 0 
            elif raid_health_info.isdigit() == False:
                influx_raid_record_fields["raid_health"] = 0 
            else:
                influx_raid_record_fields["raid_health"] = 1 
            ## "nvme_health"对于有无nvme固态判断，并输出有无报错
            nvme_get_mounted_route_command = 'lsblk|grep nvme|sed \'1d\'|awk \'{print $7}\''
            nvme_mounted_route = commands.getoutput(nvme_get_mounted_route_command)
            if nvme_mounted_route == '': 
                influx_raid_record_fields["nvme_health"] = 1 
            else:
                nvme_status_get = commands.getoutput('ls ' + nvme_mounted_route)
                if nvme_status_get == 'ls:' or '-ba':
                    influx_raid_record_fields["nvme_health"] = 1 
                elif nvme_status_get == '': 
                    influx_raid_record_fields["nvme_health"] = 0 
                else:
                    influx_raid_record_fields["nvme_health"] = 1 
            ## "physical_disk_health"通过raid卡指令判断机械硬盘状态的部分
            dell_raid_info_get_command = "/opt/MegaRAID/MegaCli/MegaCli64 -pdlist -a0|grep -iE 'slot|Non Coerced Size|firmware state|Error'"
            dell_raid_info = commands.getoutput(dell_raid_info_get_command)
            dell_raid_info_list = dell_raid_info.split('\n')
            ## 部分机器的MegaRaid位置是/opt/lsi/MegaCLI
            if len(dell_raid_info_list) < 10: 
                dell_raid_info_get_command = "/opt/lsi/MegaCLI/MegaCli64 -pdlist -a0|grep -iE 'slot|Non Coerced Size|firmware state|Error'"
                dell_raid_info = commands.getoutput(dell_raid_info_get_command)
                dell_raid_info_list = dell_raid_info.split('\n')
            dell_raid_info_list_index = 1 
            dell_raid_stats_bool = 0
            error_slot_state = ''
            while dell_raid_info_list_index < len(dell_raid_info_list):         ##正确的循环走法，按照行直接判断就行。
                if (dell_raid_info_list[dell_raid_info_list_index].split( ))[-1] == '0':
                    dell_raid_stats_bool += 0
                else:
                    if (dell_raid_info_list[dell_raid_info_list_index].split( ))[0] == 'Media':
                        dell_raid_stats_bool += 1
                        dell_error_slot_number = (dell_raid_info_list[dell_raid_info_list_index - 1].split( ))[0] + ' ' + (dell_raid_info_list[dell_raid_info_list_index - 1].split( ))[-1]
                        error_slot_state = error_slot_state.join(dell_error_slot_number + ' 存在扇区错误。')
                    elif (dell_raid_info_list[dell_raid_info_list_index].split( ))[0] == 'Other':
                        dell_raid_stats_bool += 1
                        dell_error_slot_number += (dell_raid_info_list[dell_raid_info_list_index - 2].split( ))[0] + ' ' + (dell_raid_info_list[dell_raid_info_list_index - 1].split( ))[-1]
                        error_slot_state = error_slot_state.join(dell_error_slot_number + '存在接触连接错误。')
                dell_raid_info_list_index += 1
            if dell_raid_stats_bool > 0:
                influx_raid_record_fields["physical_disk_health"] = 0       ## 存在error
            return influx_raid_record_fields,error_slot_state
        ## 当型号是R610的时候==========================================
        else:
            influx_raid_record_fields["raid_health"] = 1 
            influx_raid_record_fields["nvme_health"] = 1 
            influx_raid_record_fields["physical_disk_health"] = 2           ## 特殊情况物理盘健康指标为2，用来之后作省略判断
            error_slot_state = '本型号机器无权限或无法获取raid卡相关信息'
            return influx_raid_record_fields,error_slot_state


##========================================================================================
    ## 当server时HUAWEI的时候
    if (manufactory.split( ))[1] == 'Huawei':
        ## "raid_health"对于阵列卡状态的判断，如果
        raid_health_get_command = '/opt/MegaRAID/MegaCli/MegaCli64 -AdpAllInfo -aALL|grep -iE Virtual|awk \'{print $4}\''
        raid_health_info = commands.getoutput(raid_health_get_command)
        if raid_health_info == '':
            influx_raid_record_fields["raid_health"] = 0
        elif raid_health_info.isdigit() == False:
            influx_raid_record_fields["raid_health"] = 0
        else:
            influx_raid_record_fields["raid_health"] = 1
        ## "nvme_health"对于有无nvme固态判断，并输出有无报错
        nvme_get_mounted_route_command = 'lsblk|grep nvme|sed \'1d\'|awk \'{print $7}\''
        nvme_mounted_route = commands.getoutput(nvme_get_mounted_route_command)
        if nvme_mounted_route == '':
            influx_raid_record_fields["nvme_health"] = 1
        else:
            nvme_status_get = commands.getoutput('ls ' + nvme_mounted_route)
            if nvme_status_get == 'ls:' or '-ba':
                influx_raid_record_fields["nvme_health"] = 1
            elif nvme_status_get == '':
                influx_raid_record_fields["nvme_health"] = 0
            else:
                influx_raid_record_fields["nvme_health"] = 1
        ## "physical_disk_health"通过raid卡指令判断机械硬盘状态的部分
        huawei_raid_info_get_command = "/opt/MegaRAID/MegaCli/MegaCli64 -pdlist -a0|grep -iE 'slot|Non Coerced Size|firmware state|Error'"
        huawei_raid_info = commands.getoutput(huawei_raid_info_get_command)
        huawei_raid_info_list = huawei_raid_info.split('\n')
        huawei_raid_info_list_index = 1
        huawei_raid_stats_bool = 0
        error_slot_state = ''
        while huawei_raid_info_list_index < len(huawei_raid_info_list):
            if (huawei_raid_info_list[huawei_raid_info_list_index].split( ))[-1] == '0':
                huawei_raid_stats_bool += 0
            else:
                if (huawei_raid_info_list[huawei_raid_info_list_index].split( ))[0] == 'Media':
                    huawei_raid_stats_bool += 1
                    huawei_error_slot_number = (huawei_raid_info_list[huawei_raid_info_list_index - 1].split( ))[0] + ' ' + (huawei_raid_info_list[huawei_raid_info_list_index - 1].split( ))[-1]
                    error_slot_state = error_slot_state = huawei_error_slot_number + ' 存在扇区错误。'
                elif (huawei_raid_info_list[huawei_raid_info_list_index].split( ))[0] == 'Other':
                    huawei_raid_stats_bool += 1
                    huawei_error_slot_number = (huawei_raid_info_list[huawei_raid_info_list_index - 2].split( ))[0] + ' ' + (huawei_raid_info_list[huawei_raid_info_list_index - 2].split( ))[-1]
                    error_slot_state = error_slot_state.join(huawei_error_slot_number + ' 存在接触连接错误。')
            huawei_raid_info_list_index += 1
        if huawei_raid_stats_bool > 0:
            influx_raid_record_fields["physical_disk_health"] = 0       ## 存在error
        return influx_raid_record_fields,error_slot_state

##========================================================================================
    ## 当server是HP的时候，HP比较特殊，需要进/data/然后去具体的每个盘里面，运行dmesg|grep -IE 'I/O error',然后通过获得的dev信息再用lshw去获取slot信息。
    if (manufactory.split( ))[1] == 'HP':
        ## "raid_health"对于阵列卡状态的判断，如果
        raid_health_get_command = 'hpssacli ctrl all show status|grep Controller|awk \'{print $3}\''
        raid_health_info = commands.getoutput(raid_health_get_command)
        if raid_health_info == 'OK':
            influx_raid_record_fields["raid_health"] = 1
        else:
            influx_raid_record_fields["raid_health"] = 0
        ## "nvme_health"对于有无nvme固态判断，并输出有无报错
        nvme_get_mounted_route_command = 'lsblk|grep nvme|sed \'1d\'|awk \'{print $7}\''
        nvme_mounted_route = commands.getoutput(nvme_get_mounted_route_command)
        if nvme_mounted_route == '':
            influx_raid_record_fields["nvme_health"] = 1
        else:
            nvme_status_get = commands.getoutput('ls ' + nvme_mounted_route)
            if nvme_status_get == 'ls:' or '-ba':
                influx_raid_record_fields["nvme_health"] = 1
            elif nvme_status_get == '':
                influx_raid_record_fields["nvme_health"] = 0
            else:
                influx_raid_record_fields["nvme_health"] = 1
        ## "physical_disk_health"通过raid卡指令判断机械硬盘状态的部分
        hp_product_check_command = 'dmidecode -t 1 | grep Product|awk \'{print $3,$4,$5}\''
        hp_product = commands.getoutput(hp_product_check_command)
        if hp_product == 'ProLiant DL360p Gen8':
            hp_raid_info_get_command = "hpssacli ctrl slot=0 pd all show|grep physicaldrive"
            hp_raid_info = commands.getoutput(hp_raid_info_get_command)
            hp_raid_info_list = hp_raid_info.split('\n')
            hp_raid_info_list_index = 0
            hp_raid_stats_bool = 0
            error_slot_state = ''
            while hp_raid_info_list_index < len(hp_raid_info_list):
                if (hp_raid_info_list[hp_raid_info_list_index]).split( )[-1] == 'OK)':
                    hp_raid_stats_bool += 0
                else:
                    hp_error_slot_number = ((hp_raid_info_list[hp_raid_info_list_index]).split( )[4] + ' ' + (hp_raid_info_list[hp_raid_info_list_index]).split( )[5])[2:]
                    hp_error_slot_size = ((hp_raid_info_list[hp_raid_info_list_index]).split( )[7] + ' ' + ((hp_raid_info_list[hp_raid_info_list_index]).split( )[8])[:2])
                    hp_raid_stats_bool += 1
                    error_slot_state = error_slot_state.join(hp_error_slot_number + ' 存在扇区错误, 磁盘容量为' + hp_error_slot_size + '。')
                hp_raid_info_list_index += 1
            if hp_raid_stats_bool > 0:
                influx_raid_record_fields["physical_disk_health"] = 0       ## 存在error
            return influx_raid_record_fields,error_slot_state
        elif hp_product == 'ProLiant DL380 Gen9':
            hp_raid_info_get_command = "hpssacli ctrl slot=0 pd all show|grep physicaldrive"
            hp_raid_info = commands.getoutput(hp_raid_info_get_command)
            hp_raid_info_list = hp_raid_info.split('\n')
            hp_raid_info_list_index = 0
            hp_raid_stats_bool = 0
            error_slot_state = ''
            while hp_raid_info_list_index < len(hp_raid_info_list):
                if (hp_raid_info_list[hp_raid_info_list_index]).split( )[-1] == 'OK)':
                    hp_raid_stats_bool += 0
                else:
                    hp_error_slot_number = ((hp_raid_info_list[hp_raid_info_list_index]).split( )[4] + ' ' + (hp_raid_info_list[hp_raid_info_list_index]).split( )[5])[2:]
                    hp_error_slot_size = ((hp_raid_info_list[hp_raid_info_list_index]).split( )[7] + ' ' + ((hp_raid_info_list[hp_raid_info_list_index]).split( )[8])[:2])
                    hp_raid_stats_bool += 1
                    error_slot_state = error_slot_state.join(hp_error_slot_number + ' 存在扇区错误, 磁盘容量为' + hp_error_slot_size + '。')
                hp_raid_info_list_index += 1
            if hp_raid_stats_bool > 0:
                influx_raid_record_fields["physical_disk_health"] = 0       ## 存在error
            return influx_raid_record_fields,error_slot_state

print get_server_raid_card_metrics()[0]
print get_server_raid_card_metrics()[1]