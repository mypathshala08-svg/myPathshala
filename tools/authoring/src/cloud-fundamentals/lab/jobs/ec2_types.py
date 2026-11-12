import ijson, sys, collections, json
f = open(sys.argv[1], 'rb'); t = set()
for sku, p in ijson.kvitems(f, 'products'):
    a = p.get('attributes', {})
    if a.get('instanceType') and a.get('operatingSystem') == 'Linux' and a.get('tenancy') == 'Shared' and a.get('capacitystatus') == 'Used' and a.get('preInstalledSw') == 'NA':
        t.add(a['instanceType'])
fam = collections.Counter(x.split('.')[0][0] for x in t)
print("== instance types offered in ap-south-1 (Linux, shared):", len(t))
print("  by family letter:", dict(sorted(fam.items(), key=lambda kv: -kv[1])))
