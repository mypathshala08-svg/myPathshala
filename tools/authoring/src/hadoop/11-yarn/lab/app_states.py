# app_states.py: submit-and-watch. Polls the ResourceManager REST API every 0.2 s and prints every
# change of application state, plus how many containers the app holds. Usage: python3 app_states.py <app_id>
import json, sys, time, urllib.request
RM = "http://resourcemanager:8088/ws/v1/cluster/apps/"
app, t0, last = sys.argv[1], time.time(), None
while True:
    try:
        a = json.load(urllib.request.urlopen(RM + app))["app"]
    except Exception:
        time.sleep(0.2); continue
    now = (a["state"], a.get("finalStatus"), a.get("runningContainers", 0), a.get("allocatedMB", 0))
    if now != last:
        print(f"+{time.time() - t0:5.1f} s  state={now[0]:10} final={now[1]:9} containers={max(now[2], 0)}  allocatedMB={max(now[3], 0)}")
        last = now
    if a["state"] in ("FINISHED", "FAILED", "KILLED"):
        print("diagnostics:", (a.get("diagnostics") or "-")[:150])
        break
    time.sleep(0.2)
