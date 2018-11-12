#!/usr/bin/python
# excute once a day
import os
import commands
from metric import Metric, Metrics, Field, Gauge


def match_mod(output):
    if "round-robin" in output.lower():
        return 0
    elif "active-backup" in output.lower():
        return 1
    elif "XOR" in output:
        return 2
    elif "broadcast" in output:
        return 3
    elif "802.3ad" in output:
        return 4
    elif "adaptive transmit load " in output.lower():
        return 5
    elif "adaptive load balancing" in output.lower():
        return 6
    return -1


def get_bond_mode():
    command = "cat /proc/net/bonding/bond0  |grep 'Bonding Mode:' |awk -F ': ' '{print $2}'"
    output = commands.getoutput(command)

    metrics = Metrics()
    metrics.add(Metric("hardware.bonding", {"mode": output}, [Field(name="bond_mod", value=match_mod(output), type=Gauge)]))

    return metrics.to_string()


if __name__ == '__main__':
    if os.path.exists("/proc/net/bonding/bond0"):
        print get_bond_mode()
    else:
        exit(1)
