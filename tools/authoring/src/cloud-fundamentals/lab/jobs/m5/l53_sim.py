# Lesson 5.3 — SIMULATION (not a measurement): fixed capacity vs target-tracking elasticity over one Diwali day
import math
CAP = 100          # requests/s one m7i.large can serve at 100% CPU (assumption)
TARGET = 0.5       # keep average CPU at 50%
PRICE = 0.10605    # US$/h On-Demand m7i.large, Mumbai (real, 10 Nov 2026)
hours = list(range(24))
traffic = [40,30,25,20,20,30,80,150,220,180,160,200,320,300,180,150,200,320,600,900,1100,800,400,150]  # req/s per hour (assumed shape)
fixed = math.ceil(max(traffic) / (CAP * TARGET))           # sized for the peak, all day
print("hour  traffic  elastic_servers  fixed_servers")
el_total = 0
for h, r in zip(hours, traffic):
    n = max(2, math.ceil(r / (CAP * TARGET)))               # min 2 for two AZs
    el_total += n
    if h % 3 == 0 or r == max(traffic):
        print(f"{h:02d}:00  {r:5d}      {n:3d}              {fixed:3d}")
print(f"server-hours per day: elastic {el_total}  vs fixed {fixed*24}")
print(f"cost per day (US$):   elastic {el_total*PRICE:.2f}  vs fixed {fixed*24*PRICE:.2f}  → saving {100*(1-el_total/(fixed*24)):.0f}%")
