# counters_lab.sh: enum and dynamic counters read back by the driver; then too many counters
cd /tmp/mr9
D=/user/hadoop/data/student_orders.csv
echo "== OrderCounters (map-only, NullOutputFormat: no output files)"
hadoop jar mr9.jar OrderCounters $D > /tmp/oc.log 2>&1; echo "exit code: $?"
grep -vE "INFO|WARN" /tmp/oc.log
echo "== one dynamic counter per student (2,000 of them)"
hadoop jar mr9.jar OrderCounters -D counters.perStudent=true $D > /tmp/oc2.log 2>&1; echo "exit code: $?"
grep "job FAILED" /tmp/oc2.log
app=$(grep -o "application_[0-9_]*" /tmp/oc2.log | head -1)
yarn application -status $app 2>/dev/null | grep -A1 "Diagnostics :" | sed 's/^\s*//'
echo "-- why the map attempts failed (JobHistory REST)"
J=job_${app#application_}
curl -s http://historyserver:19888/ws/v1/history/mapreduce/jobs/$J/tasks/${J/job/task}_m_000000/attempts \
  | python3 -c 'import sys, json; t = json.load(sys.stdin)["taskAttempts"]["taskAttempt"]; t = t if isinstance(t, list) else [t]; print(next(a for a in t if a["state"] == "FAILED")["diagnostics"].splitlines()[0])'
echo "== the limit"
hdfs getconf -confKey mapreduce.job.counters.max
