#!/usr/bin/python
import commands
from metric import Metric, Metrics, dict_to_fields


def get_manufacturer():
    # dmidecode -t 1 | grep Manufacturer
    dmidecode_command = "dmidecode -t 1 | grep Manufacturer"
    output = commands.getoutput(dmidecode_command)
    manufacturer = output.split(":")[1].strip()
    return manufacturer


def get_hp_power_capacity():
    """
    # ipmitool sdr elist | grep "Power Supply"
    Power Supply 1   | 3Dh | ok  | 10.1 | 85 Watts, Presence detected
    Power Supply 2   | 40h | ok  | 10.2 | 85 Watts, Presence detected
    """
    power_amps = []

    get_power_command = 'timeout 30 ipmitool sdr elist | grep "Power Supply"'
    powers_output = commands.getoutput(get_power_command)
    outputlist = powers_output.split("\n")
    for power_output in outputlist:
        watts = power_output.split("|")[4].split(",")[0].strip().split(" ")[0]
        amps = float(watts) / 220
        power_amps.append(amps)

    power_supply_dict = {"power_supply_1": power_amps[0], "power_supply_2": power_amps[1],
                         "power_supply_total": sum(power_amps)}
    return power_supply_dict


def get_dell_power_capacity():
    """
    # ipmitool sdr elist | grep -e "Current 1" -e "Current 2"
    Current 1        | 6Ah | ok  | 10.1 | 0.60 Amps
    Current 2        | 6Bh | ok  | 10.2 | 0.60 Amps
    """

    power_amps = []

    get_power_command = 'timeout 30 ipmitool sdr elist | grep -e "Current 1" -e "Current 2"'
    powers_output = commands.getoutput(get_power_command)
    outputlist = powers_output.split("\n")
    for power_output in outputlist:
        amps = float(power_output.split("|")[4].strip().split(" ")[0])
        power_amps.append(amps)

    power_supply_dict = {"power_supply_1": power_amps[0], "power_supply_2": power_amps[1],
                         "power_supply_total": sum(power_amps)}
    return power_supply_dict


def get_huawei_power_capacity():
    """
    # ipmitool sdr elist | grep -E "(Power1|Power2)"
    Power1           | 23h | ok  | 10.96 | 114 Watts
    Power2           | 24h | ok  | 10.97 | 90 Watts
    """
    power_amps = []

    get_power_command = 'timeout 30 ipmitool sdr elist | grep -E "(Power1|Power2)"'
    powers_output = commands.getoutput(get_power_command)
    outputlist = powers_output.split("\n")
    for power_output in outputlist:
        watts = power_output.split("|")[4].strip().split(" ")[0]
        amps = float(watts) / 220
        power_amps.append(amps)

    power_supply_dict = {"power_supply_1": power_amps[0], "power_supply_2": power_amps[1],
                         "power_supply_total": sum(power_amps)}
    return power_supply_dict


def get_inspur_power_capacity():
    """
    # ipmitool sdr elist | grep -E "(PSU0_Power|PSU1_Power)"
    Power1           | 23h | ok  | 10.96 | 114 Watts
    Power2           | 24h | ok  | 10.97 | 90 Watts
    """
    power_amps = []

    get_power_command = 'timeout 30 ipmitool sdr elist | grep -E "(PSU0_Power|PSU1_Power|PS1_Power|PS2_Power)"'
    powers_output = commands.getoutput(get_power_command)
    outputlist = powers_output.split("\n")
    for power_output in outputlist:
        watts = power_output.split("|")[4].strip().split(" ")[0]
        amps = float(watts) / 220
        power_amps.append(amps)

    power_supply_dict = {"power_supply_1": power_amps[0], "power_supply_2": power_amps[1],
                         "power_supply_total": sum(power_amps)}
    return power_supply_dict


def get_power_capacity():
    power_amps = []
    manufacturer = get_manufacturer()
    if manufacturer == "HP":
        power_amps = get_hp_power_capacity()
    if manufacturer == "Dell Inc.":
        power_amps = get_dell_power_capacity()
    if manufacturer == "Huawei":
        power_amps = get_huawei_power_capacity()
    if manufacturer in ("Inspur", "Foxconn"):
        power_amps = get_inspur_power_capacity()
    return power_amps


if __name__ == "__main__":
    metrics = Metrics()
    try:
        power_amps = get_power_capacity()
        power_supply1 = power_amps.get("power_supply_1")
        power_supply2 = power_amps.get("power_supply_2")
        metrics.add(Metric('script.hardware.powersupply', {"num": "1"}, dict_to_fields({"power_supply": power_supply1})))
        metrics.add(Metric('script.hardware.powersupply', {"num": "2"}, dict_to_fields({"power_supply": power_supply2})))
    except:
        pass
    finally:
        print(metrics.to_string())
