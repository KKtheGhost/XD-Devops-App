#!/usr/bin/env python
#-*- coding: utf-8 -*-
#@Date    : 2018-11-06 16:43:06
#@Author  : Kivinsae Fang (fangwei@xindong.com)
#@QQ      : 1669815117
#@Version : 0.1.0

import re
import commands
import pathlib2
from pathlib2 import Metric, Metrics, dict_to_fields


def get_huawei_raid_card_metrics():
##Huawei and Inspur common.
    command = "/opt/MegaRAID/storcli/storcli64 /c0/bbu show |grep -A 2 -i 'Ctrl' |tail -1"
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
