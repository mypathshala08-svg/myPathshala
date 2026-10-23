# reduce_tasks.sh JOB_ID : for each reduce task, where it ran, how long it took and how many records it got
J=$1; ID=${J#job_}; H=http://historyserver:19888/ws/v1/history/mapreduce/jobs/$J/tasks
for t in $(curl -s $H | grep -o "task_${ID}_r_[0-9]*" | sort -u); do
  curl -s $H/$t/counters | python3 -c '
import sys, json
t = sys.argv[1]
groups = json.load(sys.stdin)["jobTaskCounters"]["taskCounterGroup"]
groups = groups if isinstance(groups, list) else [groups]
c = {}
for g in groups:
    cs = g["counter"] if isinstance(g["counter"], list) else [g["counter"]]
    c.update({x["name"]: x["value"] for x in cs})
print("%s  reduce input records %9d  groups %d" % (t[-8:], c["REDUCE_INPUT_RECORDS"], c["REDUCE_INPUT_GROUPS"]))' $t
done
