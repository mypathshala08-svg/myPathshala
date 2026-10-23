# sched_lab.sh BIG_QUEUE SMALL_QUEUE : a big job fills the cluster, a small job arrives 15 s later. Who waits?
# Uses Hadoop's built-in "sleep" test job: tasks that just sleep, so timings are easy to read.
# Run inside the namenode container.
T=$(ls /opt/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-client-jobclient-*-tests.jar)
export HADOOP_CLASSPATH=$T
SLEEP="yarn org.apache.hadoop.mapreduce.SleepJob -libjars $T"
BQ=${1:-default}; SQ=${2:-default}
# big: 30 map tasks of 40 s each (the cluster runs about 11 at a time)
$SLEEP -D mapreduce.job.queuename=$BQ -D mapreduce.job.name=big -m 30 -r 1 -mt 40000 -rt 1000 > /tmp/s_big.log 2>&1 &
sleep 15
# small: 2 map tasks of 5 s each
$SLEEP -D mapreduce.job.queuename=$SQ -D mapreduce.job.name=small -m 2 -r 1 -mt 5000 -rt 1000 > /tmp/s_small.log 2>&1 &
wait
for j in big small; do
  app=$(grep -o "application_[0-9_]*" /tmp/s_$j.log | head -1)
  curl -s http://resourcemanager:8088/ws/v1/cluster/apps/$app | python3 -c '
import sys, json; a = json.load(sys.stdin)["app"]
print("%-5s queue=%-12s AM waited %5.1f s, job took %6.1f s, %s, preempted containers: %s" % (sys.argv[1], a["queue"],
      (a["launchTime"] - a["startedTime"]) / 1000, a["elapsedTime"] / 1000, a["finalStatus"], a.get("numNonAMContainerPreempted", 0)))' $j
done
grep -m1 -i "preempted" /tmp/s_big.log | sed -E 's/^[0-9-]+ [0-9:]+ INFO  //' | cut -c1-160
