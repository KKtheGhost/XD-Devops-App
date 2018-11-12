#!/usr/bin/env python
# once a minute
import re
import commands
import os
from metric import Metric, Metrics, dict_to_fields


def check_media_error_count(mediaerror):
    if int(mediaerror) == 0:
        return 1
    else:
        return 0


default_raid_type = "no_raid"


def get_disk_info():
    result = commands.getoutput('lsscsi -v')
    disk_info = re.findall('/dev/sd\S+', result)
    return disk_info


def get_old_info(slot_num=None):
    if os.path.isfile('/usr/local/disk_info'):
        f = open('/usr/local/disk_info','r')
        disk_info = f.read()
        f.close()
        disk_info = eval(disk_info)
        if slot_num:
            return disk_info.get(slot_num)
        else:
            return disk_info
    else:
        return dict()


def get_common_raid_vd(manufacturer):
    if manufacturer == 'huawei':
        command_prefix = '/opt/MegaRAID/storcli/storcli64'
    elif manufacturer == 'dell':
        command_prefix = '/opt/MegaRAID/perccli/perccli64'
    command = "{0} /call /vall show".format(command_prefix)
    output = commands.getoutput(command)
    if 'RAID10' in output:
        global default_raid_type
        default_raid_type = 'RAID10'
    vdslotpattern = r'([0-9]+)/([0-9]+) +(\w+)'
    vdlist = re.findall(vdslotpattern, output)
    raid_dict = {}
    for i in range(len(vdlist)):
        raid_dict[vdlist[i][0]] = vdlist[i][2]
    return raid_dict


def get_common_raid_metrics(manufacturer):
    if manufacturer == 'huawei':
        command_prefix = '/opt/MegaRAID/storcli/storcli64'
    elif manufacturer == 'dell':
        command_prefix = '/opt/MegaRAID/perccli/perccli64'
    command = "{0} /call /eall /sall show all".format(command_prefix)
    output = commands.getoutput(command)
    slotpattern = r'([0-9]+:[0-9]+)\s+([0-9]+)\s+(\w+)\s+(\S+)\s+([0-9]+\.[0-9]+)\s+(\w+)\s+\S+\s+(\S+)'
    SNpattern = r'SN =\s+(\S+)\s'
    Merrorpattern = r'Predictive Failure Count = ([0-9]+)'
    slotlist = re.findall(slotpattern, output)
    SNlist = re.findall(SNpattern, output)
    Merrorlist = re.findall(Merrorpattern, output)

    metrics = Metrics()
    vd_raid = get_common_raid_vd(manufacturer)
    slot_num = []
    disk_info = get_disk_info()
    unrecoverable_info = commands.getoutput('{0} /call show termlog|grep "Unrecoverable medium error"'.format(command_prefix))
    unrecoverable_disk_num = set()
    hardware_info = {}
    can_write = True
    for i in re.findall('\(\w+/s\w+\)', unrecoverable_info):
        remove_disk_id = i.split("/")[-1].strip('s|)')
        slot_check_num_tmp = re.search(r'e0x(?P<value>\w+)/s\S+',i)
        slot_check_num = slot_check_num_tmp.group('value')
        slot_check_num_10 = int(slot_check_num, 16)
        slot_id = str(slot_check_num_10) + ':' + str(remove_disk_id)
        unrecoverable_disk_num.add(slot_id)
    for i in range(len(slotlist)):
        slot_num.append(slotlist[i][0])
        fields = {"health": 0}
        tags = {"slot": slotlist[i][0]}
        if slotlist[i][0] in unrecoverable_disk_num:
            fields['Unrecover'] = 1
        else:
            fields['Unrecover'] = 0

        slot_index = str(slotlist[i][0]).split(":")[-1]
        if slot_index in vd_raid:
            tags['raid_type'] = vd_raid[slot_index]
        else:
            old_disk_info = get_old_info(slotlist[i][0])
            if old_disk_info:
                tags['raid_type'] = old_disk_info.get('raid_type', default_raid_type)
            else:
                tags['raid_type'] = default_raid_type

        tags["SN"] = SNlist[i]
        tags["state"] = slotlist[i][2]
        size = slotlist[i][4] + slotlist[i][5]
        tags["size"] = size
        fields["Mediaerror"] = int(Merrorlist[i])
        if not check_media_error_count(fields["Mediaerror"]):
            fields["health"] = 0

        f1 = lambda x: 1 if x in ['UGood', 'Onln', 'JBOD', 'Rbld'] else 0
        f2 = lambda x: 0 if int(x) > 100 else 1
        f3 = lambda x: 0 if x == 'F' else 1

        if f1(slotlist[i][2]) and f2(int(Merrorlist[i])) and f3(slotlist[i][3]) and fields['Unrecover'] == 0:
            fields["health"] = 1
        if "SSD" in slotlist[i][6]:
            for each_disk in disk_info:
                smartcommand = "/usr/sbin/smartctl -A -d sat+megaraid,{0} {1}".format(slotlist[i][0].split(':')[1],each_disk)
                smartstatus, smartoutput = commands.getstatusoutput(smartcommand)
                if smartstatus == 0:
                    if "245 Unknown_Attribute" in smartoutput:
                        ssd_life_pattern = r'245 Unknown_Attribute\s+\w+\s+(?P<value>\d+)\s+(?P<worst>\d+)'
                        ssd_life = re.search(ssd_life_pattern, smartoutput)
                        if ssd_life:
                            ssd_life_remain = ssd_life.group("worst")
                            fields["ssd_life_remain_int"] = int(ssd_life_remain)
                            if int(ssd_life_remain) < 5:
                                fields["health"] = 0
                    else:
                        ssd_life_pattern = r'Media_Wearout_Indicator \w+\s+(?P<value>\d+)\s+(?P<worst>\d+)'
                        ssd_life = re.search(ssd_life_pattern, smartoutput)
                        if ssd_life:
                            ssd_life_remain = ssd_life.group("worst")
                            fields["ssd_life_remain_int"] = int(ssd_life_remain)
                            if int(ssd_life_remain) < 5:
                                fields["health"] = 0
                    break
        metrics.add(Metric("hardware.disk", tags, dict_to_fields(fields)))

        if fields.get('health') == 0:
            can_write = False
        else:
            hardware_info[tags.get('slot')] = fields
    remove_disk_check_num_tmp = commands.getoutput("{0} /call show termlog|grep Removed".format(command_prefix))
    if remove_disk_check_num_tmp:
        remove_list = set()
        for j in re.findall('enclPd=\w+', remove_disk_check_num_tmp):
            remove_disk_check_num = re.search('enclPd=\w+',j).group(0).split('=')[1]
            remove_disk_check_cmd = "{0} /call show termlog|grep Removed |grep e0x{1}".format(command_prefix, remove_disk_check_num)
            remove_disk_output = commands.getoutput(remove_disk_check_cmd)
            remove_disk_pattern = r'(e0x{0}/s[0-9]+)'.format(remove_disk_check_num)
            remove_list_tmp = re.findall(remove_disk_pattern, remove_disk_output)
            for k in remove_list_tmp:
                remove_list.add(k)
        remove_disk_id_list = []
        for record in remove_list:
            remove_disk_id = record.split("/")[-1].strip('s')
            slot_check_num_tmp = re.search(r'e0x(?P<value>\w+)/s\S+', record)
            slot_check_num = slot_check_num_tmp.group('value')
            slot_check_num_10 = int(slot_check_num, 16)
            slot_id = str(slot_check_num_10) + ':' + str(remove_disk_id)
            if slot_id not in remove_disk_id_list and slot_id not in slot_num:
                remove_disk_id_list.append(slot_id)
        for slot_id in remove_disk_id_list:
            can_write = False
            old_disk_info = get_old_info(slot_id)

            tags.update({"slot": slot_id})
            if old_disk_info:
                old_disk_info['health'] = 0
                old_disk_info['state'] = "Removed"
                metrics.add(Metric("hardware.disk", tags=tags, fields=dict_to_fields(old_disk_info)))
            else:
                tags.update({"state": "Removed"})
                metrics.add(Metric("hardware.disk", tags=tags,
                                   fields=dict_to_fields({"health": 0})))
    if can_write:
        f = open('/usr/local/disk_info', 'w')
        f.write(str(hardware_info))
        f.close()
    return metrics.to_string()


def get_slotnum():
    command = "/usr/sbin/hpssacli ctrl all show config"
    output = commands.getoutput(command)
    pslot = re.compile(r'(\w+ Slot) +(?P<slot>[0-9]+) +(.*)')
    mslot = pslot.search(output)
    slotnum = mslot.group("slot")
    slot_vd = output.split("\n")
    raid_dict = {}
    temp_dict = {}
    for line in slot_vd:
        if "array" in line:
            temp_dict = {}
        if "logicaldrive" in line:
            logicalpattern = re.compile(r'logicaldrive.+\(.+,(?P<raid>.+),.+\)')
            raid_type = logicalpattern.search(line)
            raid_raw = raid_type.group("raid")
            raid = ''
            for ch in raid_raw.split(" "):
                raid = raid + ch
        if "physicaldrive" in line:
            physicalpattern = re.compile(r'physicaldrive (?P<slot>\w+:[0-9]+:[0-9]+)')
            physical_slot = physicalpattern.search(line)
            pslot = physical_slot.group("slot")
            temp_dict[pslot] = raid
            raid_dict = dict(raid_dict, **temp_dict)
    return slotnum, raid_dict


def get_hp_raid_metrics():
    slotnum, vd_raid = get_slotnum()
    command = "/usr/sbin/hpssacli ctrl slot={0} pd all show detail".format(slotnum)
    output = commands.getoutput(command)
    slotpattern = re.compile(r'physicaldrive (?P<slot>\w+:[0-9]+:[0-9]+)')
    statuspattern = re.compile(r'\s\s+Status: (?P<state>\w+)')
    SNpattern = re.compile(r'Serial Number: (?P<SN>\w+)')
    Sizepattern = re.compile(r'\s\s+Size: (?P<Size>.*)')
    slotlist = re.findall(slotpattern, output)
    statuslist = re.findall(statuspattern, output)

    SNlist = re.findall(SNpattern, output)
    Sizelist = re.findall(Sizepattern, output)
    metrics = Metrics()
    hardware_info = {}
    can_write = True
    for i in range(len(slotlist)):
        tags = {}
        fields = {}
        tags["slot"] = slotlist[i]

        if slotlist[i] in vd_raid:
            tags['raid_type'] = vd_raid[slotlist[i]]
        else:
            old_disk_info = get_old_info(slotlist[i])
            if old_disk_info:
                tags['raid_type'] = old_disk_info.get('raid_type')
            else:
                tags['raid_type'] = default_raid_type
        tags["SN"] = SNlist[i]
        tags["state"] = statuslist[i]
        tags["size"] = Sizelist[i]
        fields["Mediaerror"] = 0
        fields["health"] = int(statuslist[i] == "OK")

        if "Solid State SATA" in output:
            DID = int(slotlist[i][-1]) - 1
            smartcommand = "/usr/sbin/smartctl -A -d cciss,{0} /dev/sda".format(DID)
            smartstatus, smartoutput = commands.getstatusoutput(smartcommand)
            if smartstatus == 0:
                if "Media_Wearout_Indicator" in smartoutput:
                    ssd_life_pattern = r'Media_Wearout_Indicator \w+\s+(?P<value>\d+)\s+(?P<worst>\d+)'
                    ssd_life = re.search(ssd_life_pattern, smartoutput)
                    if ssd_life:
                        ssd_life_remain = ssd_life.group("worst")
                        fields["ssd_life_remain_int"] = int(ssd_life_remain)
                        if int(ssd_life_remain) < 5:
                            fields["health"] = 0
        if fields.get('health') == 0:
            can_write = False
        else:
            hardware_info[tags.get('slot')] = fields
        metrics.add(Metric("hardware.disk", tags, dict_to_fields(fields)))
    if can_write:
        f = open('/usr/local/disk_info', 'w')
        f.write(str(hardware_info))
        f.close()
    return metrics.to_string()


def get_ali_raid_metrics():
    def get_size(line):
        # [0:0:0:0]    disk    ATA      MTFDDAV240TCB-1A U037  /dev/sda    240GB
        return line.split(" ")[-1]

    def get_slot(line):
        # [0:0:0:0]    disk    ATA      MTFDDAV240TCB-1A U037  /dev/sda    240GB
        num = re.findall(r"\[(\d+):", line)[0]
        if num == '0':
            return "disk_{}_os".format(num)
        else:
            return "disk_{}_data".format(int(num)-2)

    output = commands.getoutput(
        'dmesg|grep -E "\[sd[a-z]\]"|'
        'grep -E "I/O error|Medium Error|Internal target failure|Unrecovered read error"')
    if output == "":
        return "[]"

    error_map = {}  # {"sda": "io/error"}
    sd_pattern = r"\[(sd[a-z])\]"
    # "sda", "sdb"
    sd_list = set(re.findall(sd_pattern, output))
    for sd in sd_list:
        for line in output.split("\n"):
            if sd in line:
                error_map[sd] = line

    metrics = Metrics()

    disk_info_list = commands.getoutput("lsscsi --size").split("\n")
    for index, disk_info in enumerate(disk_info_list):
        # [0:0:0:0]    disk    ATA      LITEON EGT-240N9 6P3   /dev/sda
        sd_name = re.findall(r"(sd[a-z])", disk_info)[0]
        if sd_name not in error_map:
            continue
        metrics.add(Metric("hardware.disk",
                           tags={
                               "SN": commands.getoutput("smartctl -a /dev/%s|grep Serial|awk '{print $3}'" % sd_name),
                               "state": error_map[sd_name],
                               "size": get_size(disk_info),
                               "slot": get_slot(disk_info),
                               "raid_type": "aliserver no_raid",
                           },
                           fields=dict_to_fields({"health": 0})))
    return metrics.to_string()


if __name__ == '__main__':
    output = commands.getoutput("dmidecode -t system")
    if "AliServer" in output:
        print(get_ali_raid_metrics())
        exit(0)

    output = commands.getoutput("dmidecode -t 1")
    if "Dell" in output:
        print get_common_raid_metrics('dell')
    elif "HP" in output:
        print get_hp_raid_metrics()
    elif "Huawei" in output:
        print get_common_raid_metrics('huawei')
    elif "Inspur" in output:
        print get_common_raid_metrics('huawei')
    else:
        exit(1)
