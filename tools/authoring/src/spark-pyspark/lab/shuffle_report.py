"""shuffle_report.py APPNAME -> shuffle bytes per job, from the history server REST API."""
import json, sys, urllib.request
base = "http://localhost:18080/api/v1/applications"
apps = [a for a in json.load(urllib.request.urlopen(base)) if a["name"] == sys.argv[1]]
A = max(apps, key=lambda a: a["attempts"][0]["startTime"])["id"]
g = lambda p: json.load(urllib.request.urlopen(f"{base}/{A}/{p}"))
jobs = {j["jobId"]: j for j in g("jobs")}
st = {s["stageId"]: s for s in g("stages")}
for jid in sorted(jobs):
    j = jobs[jid]; ss = [st[s] for s in j["stageIds"] if s in st]
    run = [s for s in ss if s["status"] == "COMPLETE"]
    sw = sum(s["shuffleWriteBytes"] for s in run); swr = sum(s["shuffleWriteRecords"] for s in run)
    print(f"job {jid:2} stages {len(run)} run/{len(ss)} total  tasks {sum(s['numTasks'] for s in run):3}  shuffle write {sw/1024:8.1f} KiB {swr:>9,} rec  | {j.get('description', j['name'])[:52]}")
