# monitor.py: a tiny fleet monitor. Reads the JMX/REST endpoints of every NameNode and ResourceManager,
# applies alert rules, prints one line per check. Usage: python3 monitor.py [rounds] [seconds_between]
import json, sys, time, urllib.request

CLUSTERS = {                      # name: (NameNode web, ResourceManager web or None)
    "prod": ("http://namenode:9870", "http://resourcemanager:8088"),
    "dr":   ("http://nn-canteen:9870", None),
}

def get(url):
    with urllib.request.urlopen(url, timeout=5) as r:
        return json.load(r)

def nn_metrics(base):
    beans = get(base + "/jmx?qry=Hadoop:service=NameNode,name=*")["beans"]
    m = {}
    for b in beans:
        m.update(b)
    return m

def check(cluster, nn, rm):
    alerts, info = [], {}
    try:
        m = nn_metrics(nn)
    except Exception as e:
        return [f"CRIT {cluster}: NameNode not answering ({type(e).__name__})"], info
    used = 100.0 * m["CapacityUsed"] / max(m["CapacityTotal"], 1)
    info.update(live=m["NumLiveDataNodes"], dead=m["NumDeadDataNodes"], stale=m["NumStaleDataNodes"],
                used=round(used, 1), under=m["UnderReplicatedBlocks"], missing=m["MissingBlocks"],
                files=m["FilesTotal"], safemode=bool(m.get("Safemode")))
    if info["missing"] > 0:  alerts.append(f"CRIT {cluster}: {info['missing']} missing blocks")
    if info["dead"] > 0:     alerts.append(f"CRIT {cluster}: {info['dead']} dead DataNode(s)")
    if info["stale"] > 0:    alerts.append(f"WARN {cluster}: {info['stale']} stale DataNode(s) (no heartbeat for 30 s)")
    if info["under"] > 0:    alerts.append(f"WARN {cluster}: {info['under']} under-replicated blocks")
    if info["safemode"]:     alerts.append(f"CRIT {cluster}: NameNode in safe mode (read-only)")
    if used > 80:            alerts.append(f"WARN {cluster}: HDFS {used:.0f}% full")
    if rm:
        c = get(rm + "/ws/v1/cluster/metrics")["clusterMetrics"]
        mem = 100.0 * c["allocatedMB"] / max(c["totalMB"], 1)
        info.update(nodes=c["activeNodes"], unhealthy=c["unhealthyNodes"], lost=c["lostNodes"],
                    pending=c["appsPending"], running=c["appsRunning"], mem=round(mem))
        if c["unhealthyNodes"] or c["lostNodes"]:
            alerts.append(f"CRIT {cluster}: {c['unhealthyNodes']} unhealthy / {c['lostNodes']} lost NodeManagers")
        if c["appsPending"] > 0:
            alerts.append(f"WARN {cluster}: {c['appsPending']} app(s) waiting to start (cluster memory {mem:.0f}% used)")
    return alerts, info

rounds = int(sys.argv[1]) if len(sys.argv) > 1 else 1
pause = int(sys.argv[2]) if len(sys.argv) > 2 else 10
for r in range(rounds):
    stamp = time.strftime("%H:%M:%S")
    for name, (nn, rm) in CLUSTERS.items():
        alerts, info = check(name, nn, rm)
        print(f"{stamp} {name:4} " + " ".join(f"{k}={v}" for k, v in info.items()))
        for a in alerts:
            print(f"{stamp}   ALERT {a}")
    if r < rounds - 1:
        time.sleep(pause)
