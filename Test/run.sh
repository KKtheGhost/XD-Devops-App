source function.sh
export -f process_log local_path
startdate=$(sed -n '2p' roseach.conf|awk -F '=' '{print $2}')
enddate=$(sed -n '3p' roseach.conf|awk -F '=' '{print $2}')
starthour=$(sed -n '4p' roseach.conf|awk -F '=' '{print $2}')
endhour=$(sed -n '5p' roseach.conf|awk -F '=' '{print $2}')
for logname in $(<../log.txt);do
    if [[ $1 == "go" ]];then
       list_all_logs $logname $startdate $enddate $starthour $endhour| xargs -n 1 -P 4 bash -c 'process_log "$@"' _
    else 
       list_all_logs $logname $startdate $enddate $starthour $endhour
    fi
done
