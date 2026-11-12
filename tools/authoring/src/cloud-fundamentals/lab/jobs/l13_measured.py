import json, urllib.request
u = "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/ap-south-1/index.json"
d = json.load(urllib.request.urlopen(u, timeout=60))
print("== 1) AWS publishes its price list as JSON (S3, Mumbai)")
print("  publication date:", d["publicationDate"], " products:", len(d["products"]))
def price(sku):
    for t in d["terms"]["OnDemand"].get(sku, {}).values():
        for pd in t["priceDimensions"].values():
            yield pd["description"], float(pd["pricePerUnit"]["USD"]), pd["unit"], pd.get("beginRange"), pd.get("endRange")
found = {}
for sku, p in d["products"].items():
    a = p["attributes"]
    if a.get("volumeType") == "Standard" and a.get("storageClass") == "General Purpose":
        found["storage"] = list(price(sku))
    if a.get("usagetype") == "APS3-Requests-Tier1" and "requests" not in found:
        found["requests"] = list(price(sku))
print("== 2) S3 Standard storage, per GB-month (tiers)")
for desc, usd, unit, b, e in found["storage"]:
    print(f"  {b:>6}–{e:<6} GB  ${usd}  per {unit}")
print("== 3) PUT/COPY/POST/LIST requests")
for desc, usd, unit, b, e in found["requests"][:1]:
    print(f"  ${usd:.6f} per request  (= ${usd*1000:.4f} per 1,000)")
print("== 4) TiffinGo menu photos: 500 GB stored, 200,000 uploads in a month")
s = [x for x in found["storage"] if x[3] == "0"][0][1]
r = found["requests"][0][1]
print(f"  storage  500 × {s} = ${500*s:.2f}")
print(f"  requests 200000 × {r:.6f} = ${200000*r:.2f}")
print(f"  total ≈ ${500*s+200000*r:.2f} per month · if photos removed next month: $0 storage")
print("== 5) EC2 virtual machines in Mumbai: priced per hour (Linux, on-demand)")
e = json.load(open("/root/lab/cloud/captures/ec2_aps1_prices.json"))
for it in ["t4g.micro", "t3.micro", "t3.medium", "m7i.large"]:
    v = e[it]
    print(f"  {it:10} {v['vcpu']} vCPU {v['memory']:>7}  ${v['usd_hour']:.4f}/h  → 1 day ${v['usd_hour']*24:.2f} · full month ${v['usd_hour']*730:.2f}")
print("  stop it after a 2-hour lab: t3.medium costs", f"${e['t3.medium']['usd_hour']*2:.4f}")
