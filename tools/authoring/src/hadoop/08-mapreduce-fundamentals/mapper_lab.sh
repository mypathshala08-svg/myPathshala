# mapper_lab.sh: run the map-only CleanOrders job on dirty data and look at counters, output files and task logs
cd /tmp/mr
hdfs dfs -D dfs.blocksize=2097152 -put -f dirty_orders.csv /user/hadoop/data/
hdfs dfs -rm -r -f -skipTrash /out/clean > /dev/null 2>&1
hadoop jar mr.jar CleanOrders /user/hadoop/data/dirty_orders.csv /out/clean 2>&1 \
  | grep -E "number of splits|Submitted application|map 100%|completed|Launched|Map input records|Map output records|Spilled|CleanOrders|GOOD|HEADER|WRONG_FIELDS|BAD_AMOUNT"
echo "--- output files (map-only: part-m-*)"
hdfs dfs -ls /out/clean | awk '{print $5, $8}'
hdfs dfs -cat /out/clean/part-m-00000 2>/dev/null | head -3
hdfs dfs -cat /out/clean/part-m-* | grep -c "vada pav,20"     # 49,986 clean + 59 fixed from "Vada Pav "
echo "--- task logs (stderr of each map task)"
app=$(yarn application -list -appStates FINISHED 2>/dev/null | grep "clean orders" | awk '{print $1}' | tail -1)
sleep 5
yarn logs -applicationId $app -log_files stderr 2>/dev/null | grep -E "^Container: |setup\(\)|cleanup\(\)"
