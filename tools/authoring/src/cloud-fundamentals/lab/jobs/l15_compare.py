import json
e = json.load(open("/root/lab/cloud/captures/ec2_aps1_prices.json"))
usd = 84.0   # assumption: ₹ per US$ for illustration
h = e["m7i.large"]["usd_hour"]
print("== 1) real price: m7i.large (2 vCPU, 8 GiB) Linux on-demand, Mumbai: $%.5f/h" % h)
print("== 2) three ways to run 4 such servers for 3 years (₹, illustrative assumptions marked *)")
own_hw = 4 * 250000             # * buy 4 rack servers
own_run = 4 * 3 * 12 * 6000     # * power, rack space, network per server-month
own_staff = 3 * 12 * 15000      # * part-time admin share
own = own_hw + own_run + own_staff
cloud_247 = 4 * h * 24 * 365 * 3 * usd
cloud_busy = 4 * h * 10 * 300 * 3 * usd      # only 10 h/day, 300 days/year
print(f"  A) own servers (dedicated)          ₹{own:>12,.0f}  (hardware ₹{own_hw:,} up front*)")
print(f"  B) cloud, running 24×7              ₹{cloud_247:>12,.0f}  (nothing up front)")
print(f"  C) cloud, office hours only         ₹{cloud_busy:>12,.0f}  (stop at night and holidays)")
print("== 3) what the numbers say")
print("  B vs A:", "cloud cheaper" if cloud_247 < own else "own cheaper", f"by ₹{abs(own-cloud_247):,.0f}")
print("  C vs A:", "cloud cheaper" if cloud_busy < own else "own cheaper", f"by ₹{abs(own-cloud_busy):,.0f}")
print("== 4) time to get 4 new servers (typical)")
print("  own: purchase order + delivery + setup ≈ 3–8 weeks   ·   cloud: ≈ 2 minutes (API call)")
