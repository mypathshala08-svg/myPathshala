import ijson, json, sys
want = {"t3.micro", "t3.medium", "m7i.large", "t4g.micro"}
f = open(sys.argv[1], "rb")
skus = {}
for sku, p in ijson.kvitems(f, "products"):
    a = p.get("attributes", {})
    if a.get("instanceType") in want and a.get("operatingSystem") == "Linux" and a.get("tenancy") == "Shared" \
       and a.get("preInstalledSw") == "NA" and a.get("capacitystatus") == "Used" and a.get("licenseModel") == "No License required":
        skus[sku] = (a["instanceType"], a["vcpu"], a["memory"])
f.close(); f = open(sys.argv[1], "rb")
out = {}
for sku, terms in ijson.kvitems(f, "terms.OnDemand"):
    if sku in skus:
        for t in terms.values():
            for pd in t["priceDimensions"].values():
                it, cpu, mem = skus[sku]
                out[it] = dict(vcpu=cpu, memory=mem, usd_hour=float(pd["pricePerUnit"]["USD"]))
json.dump(out, open("/root/lab/cloud/captures/ec2_aps1_prices.json", "w"), indent=1)
print(out)
