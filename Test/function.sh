zone_list() {
    cat ./zones
    }
date_range () {
  FROM=$1
  TO=$2
  MATCH=$(echo $3 | sed 's/,/ /g')
  n=0
  DAY=$FROM
  while [[ $TO -gt $DAY ]]; do
    DAY=$(date -d "${FROM} + ${n} day" +%Y%m%d)
    WEEK_DAY=$(date -d $DAY +%u)
    if [[ $(echo "${MATCH}" | wc -w) -gt 0 ]];then
      for mw in ${MATCH};do
	if [ "x${mw}" == "x${WEEK_DAY}" ];then
	  echo $DAY
	fi
      done
    fi
    n=$(expr $n + 1)
  done
}


list_all_logs () {
  logname=$1
  startdate=$2
  enddate=$3
  starthour=$4
  endhour=$5
  var_date=$startdate
  var_end_date=`date -d "+1 day $enddate" +%Y%m%d`
  while [[ $var_date < $var_end_date ]];do
    addweek=$(eval date -d $var_date +%w)
    sevenday=$sevenday$addweek","
    var_date=`date -d "+1 day $var_date" +%Y%m%d`
  done
  LOG_TEMPLATE=s3://rogame-sea-vault/log/sea/FIELD_ZONE/FIELD_PROGRESS.log.FIELD_DATE-FIELD_HOUR.gz
  ZONES=$(zone_list)
  PROGRESSES=$(bash -c "echo $logname")
  DATES=$(date_range $startdate $enddate $sevenday)
  HOURS=$(bash -c "echo {${starthour}..${endhour}}")
  for z in $ZONES;do
    for p in $PROGRESSES;do
        for d in $DATES;do
	        for h in $HOURS;do
	          LOG_PATH=$(echo $LOG_TEMPLATE | sed "s+FIELD_ZONE+${z}+g" | sed "s+FIELD_PROGRESS+${p}+g" | sed "s+FIELD_DATE+${d}+g" | sed "s+FIELD_HOUR+${h}+g" )
	          echo $LOG_PATH
	        done
        done
    done
  done
}


local_path () {
  LOCAL_ROOT=/xdata/rogame-logs/
  remote=$1
  echo $remote | sed "s+^s3://rogame-sea-vault/log/+${LOCAL_ROOT}+g"
}

process_log () {
  remote=$1
  filter=$2
  locPath=$(local_path $remote)
  outName=$(echo $locPath | sed 's+\.gz$++g')
  mkdir -p $(dirname $outName)
  #aws s3 cp $remote - | gunzip | grep  '4295320516'> $outName
  aws s3 cp $remote  ${outName}.gz
}
