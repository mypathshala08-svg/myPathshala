# make_dirty.py: copy canteen_orders.csv and break some lines on purpose (same result every time)
import random
random.seed(3)
lines = open("canteen_orders.csv").read().splitlines()
bad = ["{id},dosa", "{id},chai,abc", "{id},samosa,-18", "{id},poha,25,extra", "{id},Vada Pav ,20", "order_id,item,amount"]
out = [lines[0]]
counts = {}
for line in lines[1:]:
    out.append(line)
    if random.random() < 0.001:                 # about 1 line in 1,000
        b = random.choice(bad)
        counts[b] = counts.get(b, 0) + 1
        out.append(b.format(id=900000 + len(out)))
open("dirty_orders.csv", "w").write("\n".join(out) + "\n")
print(len(out), "lines;", counts)
