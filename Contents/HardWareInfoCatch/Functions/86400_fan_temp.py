#!/usr/bin/python
# once a day

import commands
from metric import Metric, Metrics, dict_to_fields


def min_max(ol):
    min_value = "na"
    max_value = "na"
    if ol[6].strip(" ") != "na":
        min_value = float(ol[6].strip(" "))
    elif ol[5].strip(" ") != "na":
        min_value = float(ol[5].strip(" "))
    elif ol[4].strip(" ") != "na":
        min_value = float(ol[4].strip(" "))
    else:
        pass

    if ol[7].strip(" ") != "na":
        max_value = float(ol[7].strip(" "))
    elif ol[8].strip(" ") != "na":
        max_value = float(ol[8].strip(" "))
    elif ol[9].strip(" ") != "na":
        max_value = float(ol[9].strip(" "))
    else:
        pass
    min_max_dict = {'min_value': min_value, 'max_value': max_value}
    return min_max_dict


def chassis_status():
    command = 'timeout 20 ipmitool chassis status'
    status, output = commands.getstatusoutput(command)
    if status == 0:
        if "Chassis Intrusion    : inactive" in output:
            return 1
        else:
            return 0
    else:
        gentle_exit()


def gentle_exit():
    print("[]")
    exit(0)


def get_huawei_fan_temp_metrics():
    command = "timeout 20 /usr/bin/ipmitool sensor"
    status, output = commands.getstatusoutput(command)
    if status > 0:
        gentle_exit()
    outputlist = output.split("\n")
    metrics = Metrics()

    fields_temp = {'health': 1}
    fields_fan = {'health': 1}
    fields_volt = {'health': 1}
    fields_chassis = {'health': chassis_status()}
    fields_power = {'health': 1}

    tag_fan = {'FAN': 'speed', "fan_infor": ''}
    tag_temp = {'server': 'temperature', "temp_infor": ''}
    tag_volt = {'volt': 'volt', "volt_infor": ''}
    tag_chassis = {"chassis": "intrusion"}
    tag_power = {"power": "Redundancy"}

    for outinfor in outputlist:
        ol = outinfor.split("|")
        if "degrees C" in ol[2]:
            min_degrees = 0.0
            max_degrees = 100.0
            temp_dict = min_max(ol)
            if isinstance(temp_dict['min_value'], float):
                min_degrees = temp_dict['min_value']
            if isinstance(temp_dict['max_value'], float):
                max_degrees = temp_dict['max_value']

            temp = float(ol[1].strip(" "))
            if min_degrees < temp < max_degrees:
                pass
            else:
                tag_temp["temp_infor"] = tag_temp["temp_infor"] + ol[0] + ol[1]
                fields_temp['health'] = 0

        elif "Volts" in ol[2]:
            min_volt = 1
            max_volt = 1000

            volt_dict = min_max(ol)
            if isinstance(volt_dict['min_value'], float):
                min_volt = volt_dict['min_value']
            if isinstance(volt_dict['max_value'], float):
                max_volt = volt_dict['max_value']

            volt = float(ol[1].strip(" "))
            if min_volt < volt < max_volt:
                pass
            else:
                fields_volt["volt_infor"] = fields_volt["volt_infor"] + ol[0] + ol[1]
                fields_volt['health'] = 0

        elif "RPM" in ol[2]:
            speed = float(ol[1].strip(" "))
            if speed < 840:
                tag_fan["fan_infor"] = tag_fan["fan_infor"] + ol[0] + ol[1]
                fields_fan['health'] = 0

        if "PS Redundancy" in ol[0]:
            if "0x0080" in ol[3]:
                fields_power['health'] = 1

    metrics.add(Metric("hardware.fan", tag_fan, dict_to_fields(fields_fan)))
    metrics.add(Metric("hardware.temp", tag_temp, dict_to_fields(fields_temp)))
    metrics.add(Metric("hardware.volt", tag_volt, dict_to_fields(fields_volt)))
    metrics.add(Metric("hardware.chassis", tag_chassis, dict_to_fields(fields_chassis)))
    metrics.add(Metric("hardware.power", tag_power, dict_to_fields(fields_power)))
    return metrics.to_string()


def get_dell_fan_temp_metrics():
    command = "timeout 20 /usr/bin/ipmitool sensor"
    status, output = commands.getstatusoutput(command)
    if status > 0:
        gentle_exit()
    outputlist = output.split("\n")
    metrics = Metrics()

    fields_temp = {'health': 1}
    fields_fan = {'health': 1}
    fields_volt = {'health': 1}
    fields_chassis = {'health': chassis_status()}
    fields_power = {'health': 1}

    tag_fan = {'FAN': 'speed', "fan_infor": ''}
    tag_temp = {'server': 'temperature', "temp_infor": ''}
    tag_volt = {'volt': 'volt', "volt_infor": ''}
    tag_chassis = {"chassis": "intrusion"}
    tag_power = {"power": "Redundancy"}

    for outinfor in outputlist:
        ol = outinfor.split("|")
        if "degrees C" in ol[2]:
            min_degrees = 1.0
            max_degrees = 100.0
            temp_dict = min_max(ol)
            if isinstance(temp_dict['min_value'], float):
                min_degrees = temp_dict['min_value']
            if isinstance(temp_dict['max_value'], float):
                max_degrees = temp_dict['max_value']

            temp = float(ol[1].strip(" "))
            if min_degrees < temp < max_degrees:
                pass
            else:
                tag_temp["temp_infor"] = tag_temp["temp_infor"] + ol[0] + ol[1]
                fields_temp['health'] = 0

        elif "Volts" in ol[2]:
            min_volt = 1
            max_volt = 1000

            temp_dict = min_max(ol)
            if isinstance(temp_dict['min_value'], float):
                min_volt = temp_dict['min_value']
            if isinstance(temp_dict['max_value'], float):
                max_volt = temp_dict['max_value']

            volt = float(ol[1].strip(" "))
            if min_volt < volt < max_volt:
                pass
            else:
                tag_volt["volt_infor"] = tag_volt["volt_infor"] + ol[0] + ol[1]
                fields_volt['health'] = 0

        elif "RPM" in ol[2]:
            speed = float(ol[1].strip(" "))
            if speed < 840:
                tag_fan["fan_infor"] = tag_fan["fan_infor"] + ol[0] + ol[1]
                fields_fan['health'] = 0

        if "PS Redundancy" in ol[0]:
            if "0x0180" in ol[3]:
                fields_power['health'] = 1

    metrics.add(Metric("hardware.fan", tag_fan, dict_to_fields(fields_fan)))
    metrics.add(Metric("hardware.temp", tag_temp, dict_to_fields(fields_temp)))
    metrics.add(Metric("hardware.volt", tag_volt, dict_to_fields(fields_volt)))
    metrics.add(Metric("hardware.chassis", tag_chassis, dict_to_fields(fields_chassis)))
    metrics.add(Metric("hardware.power", tag_power, dict_to_fields(fields_power)))
    return metrics.to_string()


def get_hp_fan_temp_metrics():
    command = "timeout 20 /usr/bin/ipmitool sensor"
    status, output = commands.getstatusoutput(command)
    if status > 0:
        gentle_exit()
    outputlist = output.split("\n")
    metrics = Metrics()

    fields_temp = {'health': 1}
    fields_fan = {'health': 1}
    fields_volt = {'health': 1}
    fields_chassis = {'health': chassis_status()}
    fields_power = {'health': 1}

    tag_fan = {'FAN': 'speed', "fan_infor": ''}
    tag_temp = {'server': 'temperature', "temp_infor": ''}
    tag_volt = {'volt': 'volt', "volt_infor": ''}
    tag_chassis = {"chassis": "intrusion"}
    tag_power = {"power": "Redundancy"}

    for outinfor in outputlist:
        ol = outinfor.split(" | ")
        if "degrees C" in ol[2]:
            min_degrees = 1.0
            max_degrees = 100.0

            temp_dict = min_max(ol)
            if isinstance(temp_dict['min_value'], float):
                min_degrees = temp_dict['min_value']
            if isinstance(temp_dict['max_value'], float):
                max_degrees = temp_dict['max_value']

            temp = float(ol[1].strip(" "))
            if min_degrees < temp < max_degrees:
                pass
            else:
                tag_temp["temp_infor"] = tag_temp["temp_infor"] + ol[0] + ol[1]
                fields_temp['health'] = 0

        elif "percent" in ol[2]:
            speed = float(ol[1].strip(" "))
            if speed < 1:
                tag_fan["fan_infor"] = tag_fan["fan_infor"] + ol[0] + ol[1]
                fields_fan['health'] = 0
        if ("PS 1 Presence" in ol[0]) and ("0x0280" not in ol[3]):
            fields_power['health'] = 0

        if ("PS 1 Presence" in ol[0]) and ("0x0280" not in ol[3]):
            fields_power['health'] = 0

    metrics.add(Metric("hardware.fan", tag_fan, dict_to_fields(fields_fan)))
    metrics.add(Metric("hardware.temp", tag_temp, dict_to_fields(fields_temp)))
    metrics.add(Metric("hardware.volt", tag_volt, dict_to_fields(fields_volt)))
    metrics.add(Metric("hardware.chassis", tag_chassis, dict_to_fields(fields_chassis)))
    metrics.add(Metric("hardware.power", tag_power, dict_to_fields(fields_power)))
    return metrics.to_string()


if __name__ == '__main__':
    output = commands.getoutput("dmidecode -t 1")
    if "Dell" in output:
        print get_dell_fan_temp_metrics()
    elif "HP" in output:
        print get_hp_fan_temp_metrics()
    elif "Huawei" in output:
        print get_huawei_fan_temp_metrics()
    else:
        gentle_exit()
