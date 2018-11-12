#!/usr/bin/python
# once a hour
from metric import Metric, Metrics, dict_to_fields
import os
import re


def get_cpu_freq(cpu_file): 
    cpu_freq_info = open(cpu_file).read()
    
    cpu_office_hz = re.compile(r'(\d.\d+)GHz')
    cpu_hz = re.compile(r'cpu MHz\s+:\s(\d+.\d+)')
    
    cpu_hz_list = re.findall(cpu_hz, cpu_freq_info) 
    cpu_office_hz_value = re.search(cpu_office_hz,cpu_freq_info)
      
    metrics = Metrics()
    tags = {}
    fields = {}
    fields['health'] = 1
    tags['cpu'] = "frequnce"
 
    cpu_standard_freq = float(cpu_office_hz_value.group(1))*1000
    for i in cpu_hz_list:
        freq_rate = float(i)/cpu_standard_freq
        if freq_rate<0.98:
            fields['health'] = 0
            fields['freq'] = float(i)
            fields['standard_freq'] = cpu_standard_freq

    metrics.add(Metric("hardware.cpu_freq", tags, dict_to_fields(fields)))
    return metrics.to_string()


if __name__ == '__main__':
    if os.path.exists("/proc/cpuinfo"): 
        print get_cpu_freq("/proc/cpuinfo")    
    else:
        exit(1)

