# shuffle_lab.sh: watch the map-side sort buffer spill to disk, and the reducer fetch map outputs
cd /tmp/mr
for mb in 16 64 200; do
  hdfs dfs -rm -r -f -skipTrash /out/shuf_$mb > /dev/null 2>&1
  start=$(date +%s)
  hadoop jar mr.jar ItemRevenue -D mapreduce.task.io.sort.mb=$mb \
      /user/hadoop/data/orders_x30.csv /out/shuf_$mb > /tmp/shuf_$mb.log 2>&1
  app=$(grep -o "application_[0-9_]*" /tmp/shuf_$mb.log | head -1)
  echo "== io.sort.mb=$mb   job took $(( $(date +%s) - start )) s"
  grep -E "Map output records|Map output materialized bytes|Spilled Records|Reduce shuffle bytes|Total time spent by all map tasks" /tmp/shuf_$mb.log | sed 's/^\s*/  /'
  sleep 8
  yarn logs -applicationId $app -log_files syslog 2>/dev/null > /tmp/shuf_$mb.syslog
  echo "  spills written by the map task: $(grep -c 'Finished spill' /tmp/shuf_$mb.syslog)"
done
echo "== map task log (io.sort.mb=16), first lines about the sort buffer"
grep -E "mapreduce.task.io.sort.mb|soft limit|Spilling map output|Finished spill 0" /tmp/shuf_16.syslog | head -4 | cut -c25-150
echo "== map task log (io.sort.mb=16): merging the spill files into one sorted output"
grep -E "Finished spill 17|Merging|merge-pass" /tmp/shuf_16.syslog | cut -c25-170
echo "== reducer input is sorted by key"
hdfs dfs -cat /out/shuf_16/part-r-00000
