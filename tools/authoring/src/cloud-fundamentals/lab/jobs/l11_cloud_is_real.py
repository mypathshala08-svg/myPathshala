import json, urllib.request, collections, time
def get(u):
    t=time.time(); d=json.load(urllib.request.urlopen(u, timeout=30)); return d, time.time()-t
print("== 1) AWS publishes every public IP range it owns")
a,_=get("https://ip-ranges.amazonaws.com/ip-ranges.json")
p=a["prefixes"]; regs=sorted({x["region"] for x in p if x["region"]!="GLOBAL"})
print("  file created:", a["createDate"], " IPv4 prefixes:", len(p), " IPv6 prefixes:", len(a["ipv6_prefixes"]))
print("  regions in the file:", len(regs))
print("  India regions:", [r for r in regs if r in ("ap-south-1","ap-south-2")], "(Mumbai, Hyderabad)")
m1=[x for x in p if x["region"]=="ap-south-1"]
print("  ap-south-1 IPv4 entries:", len(m1), " unique ranges:", len({x['ip_prefix'] for x in m1}))
svc=collections.Counter(x["service"] for x in p if x["region"]=="ap-south-1")
print("  services with ranges in ap-south-1 (Mumbai):", dict(sorted(svc.items(), key=lambda kv:-kv[1])[:8]))
print("== 2) Google Cloud does the same")
g,_=get("https://www.gstatic.com/ipranges/cloud.json")
gs=sorted({x["scope"] for x in g["prefixes"]})
print("  prefixes:", len(g["prefixes"]), " scopes (regions):", len(gs))
print("  India scopes:", [s for s in gs if s in ("asia-south1","asia-south2")], "(Mumbai, Delhi)")
print("== 3) one example range each")
m=[x for x in p if x["region"]=="ap-south-1" and x["service"]=="EC2"][0]
print("  AWS :", m["ip_prefix"], m["region"], m["service"])
gg=[x for x in g["prefixes"] if x["scope"]=="asia-south1"][0]
print("  GCP :", gg.get("ipv4Prefix") or gg.get("ipv6Prefix"), gg["scope"])
