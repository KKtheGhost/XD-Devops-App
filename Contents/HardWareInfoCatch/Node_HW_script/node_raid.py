#!/usr/bin/env python
#-*- coding: utf-8 -*-
#@Date    : 2018-11-06 16:43:06
#@Author  : Kivinsae Fang (fangwei@xindong.com)
#@QQ      : 1669815117
#@Version : 0.1.0

import re
import commands
import pathlib2

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
        ## 当型号是R720的时候==========================================
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
            nvme_status_get = commands.getoutput('ls ' + nvme_mounted_route)
            if nvme_status == 'ls:' or '-ba':
                influx_raid_record_fields["nvme_health"] = 1
            elif nvme_status == '':
                influx_raid_record_fields["nvme_health"] = 0
            else:
                influx_raid_record_fields["nvme_health"] = 1
            ## "physical_disk_health"通过raid卡指令判断机械硬盘状态的部分
            dell_raid_info_get_command = "/opt/MegaRAID/MegaCli/MegaCli64 -pdlist -a0|grep -iE 'slot|Non Coerced Size|firmware state|Error'"
            dell_raid_info = commands.getoutput(dell_raid_info_get_command)
            dell_raid_info_list = dell_raid_info[dell_raid_info_index].split('\n')
            dell_raid_info_list_index = 1
            while dell_raid_info_list_index < len(dell_raid_info_list):
                if (dell_raid_info_list[dell_raid_info_list_index].split( ))[3] != '0' and (dell_raid_info_list[dell_raid_info_list_index].split( ))[0] == 'Media':
                    influx_raid_record_fields["physical_disk_health"] = 0
                    dell_error_slot_number = (dell_raid_info_list[dell_raid_info_list_index - 1].split( ))[0] + ' ' + (dell_raid_info_list[dell_raid_info_list_index - 1].split( ))[2]
                    error_slot_state = dell_error_slot_number + ' 存在扇区错误'
                    if (dell_raid_info_list[dell_raid_info_list_index + 1].split( ))[3] != '0' and (dell_raid_info_list[dell_raid_info_list_index].split( ))[0] == 'Other':
                        error_slot_state.join('和接触连接错误')
                else:
                    influx_raid_record_fields["physical_disk_health"] = 0
                    error_slot_state = 'OK'
            return influx_raid_record_fields,error_slot_state
        ## 当型号是R610的时候==========================================
        elif (dell_product.split( ))[3] == 'R610':
            influx_raid_record_fields["raid_health"] = 1
            influx_raid_record_fields["nvme_health"] = 1
            influx_raid_record_fields["physical_disk_health"] = 1
            return '本型号机器无法获取raid卡相关信息'
        ## 当型号是R410的时候==========================================
        elif (dell_product.split( ))[3] == 'R410':


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
        nvme_status_get = commands.getoutput('ls ' + nvme_mounted_route)
        if nvme_status == 'ls:' or '-ba':
            influx_raid_record_fields["nvme_health"] = 1
        elif nvme_status == '':
            influx_raid_record_fields["nvme_health"] = 0
        else:
            influx_raid_record_fields["nvme_health"] = 1
        ## "physical_disk_health"通过raid卡指令判断机械硬盘状态的部分
        huawei_raid_info_get_command = "/opt/MegaRAID/MegaCli/MegaCli64 -pdlist -a0|grep -iE 'slot|Non Coerced Size|firmware state|Error'"
        huawei_raid_info = commands.getoutput(huawei_raid_info_get_command)
        huawei_raid_info_list = huawei_raid_info[huawei_raid_info_index].split('\n')
        huawei_raid_info_list_index = 1
        while huawei_raid_info_list_index < len(huawei_raid_info_list):
            if (huawei_raid_info_list[huawei_raid_info_list_index].split( ))[3] != '0' and (huawei_raid_info_list[huawei_raid_info_list_index].split( ))[0] == 'Media':
                influx_raid_record_fields["physical_disk_health"] = 0
                huawei_error_slot_number = (huawei_raid_info_list[huawei_raid_info_list_index - 1].split( ))[0] + ' ' + (huawei_raid_info_list[huawei_raid_info_list_index - 1].split( ))[2]
                error_slot_state = huawei_error_slot_number + ' 存在扇区错误'
                if (huawei_raid_info_list[huawei_raid_info_list_index + 1].split( ))[3] != '0' and (huawei_raid_info_list[huawei_raid_info_list_index].split( ))[0] == 'Other':
                    error_slot_state.join('和接触连接错误')
            else:
                influx_raid_record_fields["physical_disk_health"] = 0
                error_slot_state = 'OK'
        return influx_raid_record_fields,error_slot_state


##========================================================================================
    ## 当server是HP的时候，HP比较特殊，需要进/data/然后去具体的每个盘里面，运行dmesg|grep -IE 'I/O error',然后通过获得的dev信息再用lshw去获取slot信息。
    if (manufactory.split( ))[1] == 'HP':

    raid_info_get_command = "/opt/MegaRAID/MegaCli/MegaCli64 -pdlist -a0|grep -iE 'slot|Non Coerced Size|firmware state|Error'"
    output = commands.getoutput(command)
    fields = {"health": 1}
    tags = {}
    if "use /cx/cv" in output:
        command = "/opt/MegaRAID/storcli/storcli64 /c0/cv show|grep -E -i 'Model|Ctrl' -A 2 |tail -1"
        output = commands.getoutput(command)
        if "Optimal" in output:
            fields["health"] = 1
        else:
            fields["health"] = 0
    elif "Battery is absent!" in output:
        fields["health"] = 1
    tags["status"] = output
    metrics = Metrics()
    metrics.add(Metric("hardware.raid_card_battery", tags, dict_to_fields(fields)))
    return metrics.to_string()

##========================================================================================
##========================================================================================

def get_dell_raid_card_metrics():
    command = "/opt/MegaRAID/perccli/perccli64 /c0/bbu show |grep -A 2 -i 'Ctrl' |tail -1"
    output = commands.getoutput(command)
    fields = {"health": 1}
    tags = {}
    if "use /cx/cv" in output:
        command = "/opt/MegaRAID/perccli/perccli64 /c0/cv show|grep -E -i 'Model|Ctrl' -A 2 |tail -1"
        output = commands.getoutput(command)
        if "Optimal" in output:
            fields["health"] = 1
        else:
            fields["health"] = 0
    elif "Battery is absent!" in output:
        fields["health"] = 1
        tags["status"] = output

    no_battery_model_list = ['H310', 'H330', 'HBA330']
    model_command = "/opt/MegaRAID/perccli/perccli64 /c0 show | grep 'Product Name'"
    model_output = commands.getoutput(model_command)

    for model in no_battery_model_list:
        if model in model_output:
            fields["health"] = 1
            tags["status"] = 'This raid card do not have battery!'

    metrics = Metrics()
    metrics.add(Metric("hardware.raid_card_battery", tags, dict_to_fields(fields)))
    return metrics.to_string()


def get_slotnum():
    command = "/usr/sbin/hpssacli ctrl all show config"
    slot = commands.getoutput(command)

    pslot = re.compile(r'(\w+ Slot) +(?P<slot>[0-9]+) +(.*)')
    mslot = pslot.search(slot)
    slotnum = mslot.group("slot")
    return slotnum


def get_hp_raid_card_metrics(): ## 惠普Raid卡信息获取
    slotnum = get_slotnum()
    battery_command = "/usr/sbin/hpssacli ctrl slot={0} show | grep 'Battery/Capacitor Status:'".format(slotnum)
    cache_command = "/usr/sbin/hpssacli ctrl slot={0} show | grep 'Cache Status:'".format(slotnum)

    battery_result = commands.getoutput(battery_command)
    if ": " in battery_result:
        battery_result = battery_result.split(": ")[1]
    else:
        battery_result = "No battery status"

    cache_result = commands.getoutput(cache_command).split(": ")[1]
    fields = {}
    tags = {}
    if "OK" in cache_result:
        if "Recharging" in battery_result or "OK" in battery_result:
            fields["health"] = 1
            tags["status"] = cache_result
        else:
            fields["health"] = 0
            tags["status"] = "Battery: " + battery_result
    else:
        fields["health"] = 0
        tags["status"] = "Cache: " + cache_result

    metrics = Metrics()
    metrics.add(Metric("hardware.raid_card_battery", tags, dict_to_fields(fields)))
    return metrics.to_string()


if __name__ == '__main__':
    output = commands.getoutput("dmidecode -t 1")
    if "Dell" in output:
        print get_dell_raid_card_metrics()
    elif "HP" in output:
        print get_hp_raid_card_metrics()
    elif "Huawei" in output:
        print get_huawei_raid_card_metrics()
    elif "Inspur" in output:
        print get_huawei_raid_card_metrics()
    else:
        exit(1)
