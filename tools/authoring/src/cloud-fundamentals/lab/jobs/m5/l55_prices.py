# Lesson 5.5 — real AWS prices for Mumbai (ap-south-1), Linux, from AWS's public price files
# on-demand: AWS Price List API (ec2_aps1_prices.json, 10 Nov 2026); Savings Plans: AWSComputeSavingsPlan offer file
# (published 2026-11-09); Spot: the public feed behind the EC2 Spot pricing page (snapshot 10 Nov 2026)
import json
od = json.load(open('/root/lab/cloud/captures/ec2_aps1_prices.json'))
sp = {('t3.micro','csp1'):0.0081,('t3.micro','csp3'):0.0054,('t3.micro','isp1'):0.0071,('t3.micro','isp3'):0.0047,('t3.micro','spot'):0.0028,
      ('m7i.large','csp1'):0.07828,('m7i.large','csp3'):0.0533,('m7i.large','isp1'):0.07004,('m7i.large','isp3'):0.04822,('m7i.large','spot'):0.0442}
INR = 88   # assumption: ₹ per US$ — check today's rate
H = 730    # hours in an average month
print("== 1) one instance, running all month (730 h), Mumbai, Linux, US$/hour → ₹/month")
for t in ['t3.micro', 'm7i.large']:
    base = od[t]['usd_hour']
    print(f"{t}  ({od[t]['vcpu']} vCPU, {od[t]['memory']})")
    for k, name in [('od','On-Demand'),('csp1','Compute Savings Plan 1 yr, no upfront'),('csp3','Compute Savings Plan 3 yr, no upfront'),
                    ('isp1','EC2 Instance Savings Plan 1 yr, no upfront'),('isp3','EC2 Instance Savings Plan 3 yr, no upfront'),('spot','Spot (price at snapshot time)')]:
        p = base if k == 'od' else sp[(t, k)]
        print(f"  {name:44s} ${p:<8.5f}/h  ₹{p*H*INR:8.0f}/month  saving {100*(1-p/base):3.0f}%")
print("== 2) the Diwali week: 10 extra m7i.large for 7 days × 6 evening hours only")
h = 10 * 7 * 6
print(f"  instance-hours: {h}  on-demand cost: ${h*od['m7i.large']['usd_hour']:.2f} (≈ ₹{h*od['m7i.large']['usd_hour']*INR:.0f})")
print(f"  same 10 servers bought and kept all year on-prem: you pay for {10*8760} hours of capacity")
# data transfer + S3 tiers: AWSDataTransfer and AmazonS3 offer files for ap-south-1 (fetched 11 Nov 2026)
print("== 3) data transfer OUT to the internet from Mumbai: TiffinGo serves 2 TB of photos a month")
gb = 2048; free = 100; rate = 0.1093
print(f"  data IN: free   first {free} GB/month out: free (global, all Regions)   next 10 TB: ${rate}/GB")
print(f"  ({gb} - {free}) GB × ${rate} = ${(gb-free)*rate:.2f}/month (≈ ₹{(gb-free)*rate*INR:.0f})")
print(f"  same photos through CloudFront to India edge: priced per GB by CloudFront instead; origin→CloudFront transfer is free")
print("== 4) tiered storage price: S3 Standard, Mumbai, per GB-month")
for lo, hi, p in [(0, 50, 0.025), (50, 500, 0.024), (500, None, 0.023)]:
    print(f"  {lo:>4} TB – {str(hi)+' TB' if hi else 'more':>7}: ${p}")
for name, p in [('S3 Standard-IA', 0.0138), ('S3 One Zone-IA', 0.011), ('S3 Glacier Instant Retrieval', 0.005), ('S3 Glacier Flexible Retrieval', 0.0045)]:
    print(f"  {name:30s} ${p}/GB-month  ({100*(1-p/0.025):.0f}% cheaper than Standard)")
print("== 5) three years of one always-on m7i.large: total compute cost")
for k, name in [('od','On-Demand'),('csp3','Compute Savings Plan 3 yr'),('isp3','EC2 Instance Savings Plan 3 yr')]:
    p = od['m7i.large']['usd_hour'] if k == 'od' else sp[('m7i.large', k)]
    print(f"  {name:32s} ${p*H*36:8.0f}  (≈ ₹{p*H*36*INR:,.0f})")
