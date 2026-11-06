import json, sys, urllib.request
base = "http://localhost:18080/api/v1/applications"
apps = json.load(urllib.request.urlopen(base))
app = next(a for a in apps if a["name"] == sys.argv[1])
A = app["id"]; g = lambda p: json.load(urllib.request.urlopen(f"{base}/{A}/{p}"))
print("application", A, "duration", round(app["attempts"][0]["duration"] / 1000, 1), "s")
print("\nJOBS")
for j in sorted(g("jobs"), key=lambda j: j["jobId"]):
    print(f"  job {j['jobId']}: stages {j['stageIds']} tasks {j['numTasks']:>3} skipped-stages {j['numSkippedStages']}  {j.get('description', j['name'])[:48]}")
print("\nSTAGES")
for s in sorted(g("stages"), key=lambda s: s["stageId"]):
    print(f"  stage {s['stageId']}: {s['status']:8} tasks {s['numTasks']:>3}  shuffle write {s['shuffleWriteBytes']/1024:7.1f} KiB  read {s['shuffleReadBytes']/1024:7.1f} KiB")
print("\nEXECUTORS")
for e in g("executors"):
    print(f"  {e['id']:>6} {e['hostPort']:22} cores {e['totalCores']}  tasks {e['totalTasks']:>3}  task time {e['totalDuration']/1000:5.1f} s")
