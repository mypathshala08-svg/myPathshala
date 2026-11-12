import json, urllib.request, collections
from datetime import datetime, timezone, timedelta
inc = json.load(urllib.request.urlopen("https://status.cloud.google.com/incidents.json", timeout=60))
now = datetime(2026, 11, 10, tzinfo=timezone.utc)
yr = [i for i in inc if datetime.fromisoformat(i["begin"]) > now - timedelta(days=365)]
print("== 1) Google Cloud publishes every incident (status.cloud.google.com)")
print("  incidents in the file:", len(inc), " in the last 12 months:", len(yr))
print("== 2) last 12 months by severity")
print(" ", dict(collections.Counter(i.get("severity", "?") for i in yr)))
def dur(i):
    return (datetime.fromisoformat(i["end"]) - datetime.fromisoformat(i["begin"])).total_seconds() / 3600 if i.get("end") else None
d = sorted([x for x in ((dur(i), i) for i in yr) if x[0] is not None], key=lambda x: x[0])
hrs = [x[0] for x in d]
print("== 3) how long incidents lasted (hours)")
print(f"  median {hrs[len(hrs)//2]:.1f} h · 90th percentile {hrs[int(len(hrs)*0.9)]:.1f} h · longest {hrs[-1]:.1f} h")
print("== 4) incidents that touched Indian regions (asia-south1 Mumbai / asia-south2 Delhi)")
ind = [i for i in yr if any(l.get("id") in ("asia-south1", "asia-south2") for l in i.get("currently_affected_locations", []) + i.get("previously_affected_locations", []))]
print("  count:", len(ind))
for i in ind[:3]:
    print("  -", i["begin"][:10], "|", i["external_desc"][:70])
print("== 5) most affected products (last 12 months)")
c = collections.Counter(p["title"] for i in yr for p in i.get("affected_products", []))
for k, v in c.most_common(5): print(f"  {v:3d}  {k}")
