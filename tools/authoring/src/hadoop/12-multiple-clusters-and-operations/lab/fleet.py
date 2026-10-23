# fleet.py: an inventory of every cluster we run - the first thing a platform team builds.
import json, urllib.request
NAMENODES = {"prod (lab8)": "http://namenode:9870",
             "dr (lab72) ns canteen": "http://nn-canteen:9870",
             "dr (lab72) ns hostel": "http://nn-hostel:9870"}
def jmx(base, name):
    return json.load(urllib.request.urlopen(f"{base}/jmx?qry=Hadoop:service=NameNode,name={name}", timeout=5))["beans"][0]
print(f"{'cluster':24} {'version':8} {'clusterId':38} {'live DNs':>8} {'files':>7} {'used':>9}")
for name, base in NAMENODES.items():
    info, st = jmx(base, "NameNodeInfo"), jmx(base, "FSNamesystemState")
    print(f"{name:24} {info['Version'].split(',')[0]:8} {info['ClusterId']:38} {st['NumLiveDataNodes']:>8} "
          f"{st['FilesTotal']:>7} {st['CapacityUsed'] / 2**20:>7.0f} MB")
