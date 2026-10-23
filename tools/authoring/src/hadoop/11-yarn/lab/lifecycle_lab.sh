# lifecycle_lab.sh: watch a YARN application move through its states, then kill one
cd /tmp/mr
run_and_watch() {   # output dir, extra args
  hdfs dfs -rm -r -f -skipTrash $1 > /dev/null 2>&1
  hadoop jar mr.jar ItemRevenue $2 /user/hadoop/data/orders_x30.csv $1 > /tmp/lc.log 2>&1 &
  until app=$(grep -o "application_[0-9_]*" /tmp/lc.log | head -1) && [ -n "$app" ]; do sleep 0.1; done
  echo "submitted $app"
  python3 /tmp/mr/app_states.py $app
}
echo "== 1. a normal job"
run_and_watch /out/lc1 ""
wait
echo "-- the same app as YARN reports it afterwards"
yarn application -status $(grep -o "application_[0-9_]*" /tmp/lc.log | head -1) 2>/dev/null | grep -E "Application-Type|Queue|State|Final-State|Start-Time|Finish-Time|Progress|AM Host|Aggregate Resource" | sed 's/^\s*//'
echo "== 2. kill a job while it runs"
hdfs dfs -rm -r -f -skipTrash /out/lc2 > /dev/null 2>&1
hadoop jar mr.jar ItemRevenue /user/hadoop/data/orders_x30.csv /out/lc2 > /tmp/lc2.log 2>&1 &
until app=$(grep -o "application_[0-9_]*" /tmp/lc2.log | head -1) && [ -n "$app" ]; do sleep 0.1; done
python3 /tmp/mr/app_states.py $app &
sleep 15; yarn application -kill $app 2>&1 | grep -v INFO
wait
grep -E "Job .* failed|killed|KILLED" /tmp/lc2.log | sed -E 's/^[0-9-]+ [0-9:]+ INFO  //' | head -2
echo "== 3. ask for an AM bigger than any node (3 GB on 2 GB NodeManagers)"
hadoop jar mr.jar ItemRevenue -D yarn.app.mapreduce.am.resource.mb=3072 /user/hadoop/data/canteen_orders.csv /out/lc3 2>&1 | grep -E "Exception|Invalid" | head -2 | cut -c1-250
