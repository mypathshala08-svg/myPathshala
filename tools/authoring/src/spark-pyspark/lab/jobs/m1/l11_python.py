from functools import reduce
orders = [("Mumbai", 530), ("Pune", 210), ("Mumbai", 480), ("Delhi", 990), ("Pune", 120)]
big = list(filter(lambda o: o[1] >= 300, orders))           # keep orders of 300 or more
gst = list(map(lambda o: (o[0], round(o[1] * 0.05, 2)), big)) # 5% GST on each
total = reduce(lambda a, b: a + b, [g for _, g in gst])       # add them up
by_city = {}
for city, amt in orders:                                      # group by city
    by_city[city] = by_city.get(city, 0) + amt
print("filter :", big)
print("map    :", gst)
print("reduce :", total)
print("groupBy:", dict(sorted(by_city.items(), key=lambda kv: -kv[1])))
