# Lesson 5.4 — SLA arithmetic: allowed downtime, composite availability, service credits
M = 30 * 24 * 60   # minutes in a 30-day month
Y = 365 * 24 * 60
print("== 1) what each number of nines allows")
for a in [99.0, 99.5, 99.9, 99.95, 99.99, 99.999]:
    d = (100 - a) / 100
    print(f"  {a:7.3f}%  → {d*M:7.1f} min/month   {d*Y/60:6.2f} h/year")
print("== 2) chain of components (all must work): web 99.99 × app 99.99 × db 99.95")
s = 0.9999 * 0.9999 * 0.9995
print(f"  composite = {s*100:.3f}%  → {(1-s)*M:.1f} min/month (lower than the weakest link)")
print("== 3) redundancy (either copy may work): two instances, each 99.5% (EC2 instance-level SLA)")
p = 1 - (1 - 0.995) ** 2
print(f"  composite = {p*100:.4f}%  → {(1-p)*M:.2f} min/month (if failures are independent)")
print("== 4) EC2 service credit for a bad month (Region-level SLA, 99.99% commitment)")
bill = 1000.0
for up in [99.995, 99.95, 98.5, 94.0]:
    credit = 0 if up >= 99.99 else (10 if up >= 99.0 else (30 if up >= 95.0 else 100))
    print(f"  uptime {up:6.3f}%  → credit {credit:3d}% of the affected EC2 bill = ${bill*credit/100:7.2f} of ${bill:.0f}")
