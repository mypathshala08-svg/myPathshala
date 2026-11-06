import time, json, urllib.request
def mk(spark):
    sc = spark.sparkContext
    def stages():
        return json.load(urllib.request.urlopen(f"{sc.uiWebUrl}/api/v1/applications/{sc.applicationId}/stages?details=false"))
    def run(label, f):
        b = {s["stageId"] for s in stages()}
        t = time.time(); f(); el = time.time() - t
        new = [s for s in stages() if s["stageId"] not in b and s["status"] == "COMPLETE"]
        sp = sum(s['memoryBytesSpilled'] for s in new)/2**20; dk = sum(s['diskBytesSpilled'] for s in new)/2**20
        print(f"{label:42}: {el:5.2f} s, tasks {sum(s['numTasks'] for s in new):4}, spill mem {sp:6.1f} MiB disk {dk:5.1f} MiB")
        return new
    return stages, run
