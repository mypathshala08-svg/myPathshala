# attempts.sh JOB_ID : every task attempt of a finished job (node, time, state), from the JobHistory REST API
J=$1; ID=${J#job_}
for kind in m r; do
  for t in $(curl -s http://historyserver:19888/ws/v1/history/mapreduce/jobs/$J/tasks | grep -o "task_${ID}_${kind}_[0-9]*" | sort -u); do
    curl -s http://historyserver:19888/ws/v1/history/mapreduce/jobs/$J/tasks/$t/attempts | python3 -c '
import sys, json
t = json.load(sys.stdin)["taskAttempts"]["taskAttempt"]
for a in (t if isinstance(t, list) else [t]):
    node = a["nodeHttpAddress"].split(":")[0]
    print("%-40s %-9s %-8s %5.1f s  %s" % (a["id"], a["state"], node, a["elapsedTime"] / 1000, a.get("diagnostics", "")[:70]))'
  done
done
