import zipfile, json, re, collections, glob
z = zipfile.ZipFile(glob.glob('/tmp/bc/botocore-*.whl')[0])
ver = z.filename.split('-')[1]
names = z.namelist()
svc = collections.defaultdict(set)
for n in names:
    m = re.match(r'botocore/data/([^/]+)/(\d{4}-\d{2}-\d{2})/service-2\.json', n)
    if m: svc[m.group(1)].add(m.group(2))
print(f"== 1) services the AWS SDK (botocore {ver}) knows today:", len(svc))
first = {s: min(v) for s, v in svc.items()}
by_year = collections.Counter(int(d[:4]) for d in first.values())
print("== 2) services by year of their oldest API version (a rough launch timeline)")
run = 0
for y in sorted(by_year):
    run += by_year[y]
    print(f"  {y}: +{by_year[y]:3d}  total {run:3d}  " + "#" * (by_year[y] // 3))
print("== 3) the oldest APIs")
for s, d in sorted(first.items(), key=lambda kv: kv[1])[:6]:
    print(f"  {d}  {s}")
ep = json.loads(z.read('botocore/data/endpoints.json'))
aws = [p for p in ep['partitions'] if p['partition'] == 'aws'][0]
print("== 4) commercial AWS regions listed in the SDK:", len(aws['regions']))
for r, d in aws['regions'].items():
    if r in ('ap-south-1', 'ap-south-2'): print(f"  {r:12} {d['description']}")
