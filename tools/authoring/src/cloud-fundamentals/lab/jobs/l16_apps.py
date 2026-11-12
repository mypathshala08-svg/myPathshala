import urllib.request, re, collections
h = urllib.request.urlopen("https://registry.opendata.aws/", timeout=60).read().decode()
names = re.findall(r'<h3><a href="/([^/"]+)/">', h)
tags = re.findall(r'class="label label-info tag link-tag">([^<]+)', h)
print("== 1) Registry of Open Data on AWS: public datasets anyone can use")
print("  datasets on the page:", len(set(names)) or "n/a", " tag uses:", len(tags))
print("== 2) top 15 topics (tags)")
for k, v in collections.Counter(t.strip() for t in tags).most_common(15):
    print(f"  {v:4d}  {k}")
print("== 3) a few datasets about earth, health and cities")
for n in [x for x in dict.fromkeys(names) if any(w in x for w in ("sentinel", "landsat", "noaa", "covid", "osm", "1000genomes"))][:6]:
    print("  -", n)
