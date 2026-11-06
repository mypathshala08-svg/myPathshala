# TiffinGo sizing: what a managed (or self-run) cluster must handle
import math
peak_msgs, size_kb, retention_days, rf = 20000, 1.0, 7, 3
avg_ratio, compression = 0.4, 0.5          # average/peak, zstd-ish
consumer_groups = 4
mbps_in = peak_msgs * size_kb / 1024
mbps_out = mbps_in * consumer_groups
stored_tb = peak_msgs * avg_ratio * size_kb * compression * 86400 * retention_days * rf / 1024**3
print("== 1) workload")
print(f"  peak {peak_msgs:,} msg/s x {size_kb} KB = {mbps_in:.1f} MB/s in, {mbps_out:.1f} MB/s out ({consumer_groups} groups)")
print(f"  replication traffic (RF {rf}): {mbps_in*(rf-1):.1f} MB/s between brokers")
print(f"  storage for {retention_days} days (avg {avg_ratio:.0%} of peak, compression {compression}, RF {rf}): {stored_tb:.2f} TB")
print("== 2) partitions (target 10 MB/s per partition on the slowest side)")
per_p = 10
print(f"  producer side: {math.ceil(mbps_in/per_p)}  consumer side (1 group): {math.ceil(mbps_in/per_p)}  max consumers wanted: 24")
print(f"  choose: {max(math.ceil(mbps_in/per_p), 24)} partitions (room for 24 parallel consumers)")
print("== 3) the same need, three ways to pay (shape, not prices)")
for name, unit in [("serverless (pay per GB/partition-hour)", "elastic, scale to zero-ish"), ("provisioned brokers (pay per broker-hour + storage)", "fixed capacity, you size"), ("BYOC (vendor runs it in your account)", "data stays in your VPC")]:
    print(f"  {name}: {unit}")
