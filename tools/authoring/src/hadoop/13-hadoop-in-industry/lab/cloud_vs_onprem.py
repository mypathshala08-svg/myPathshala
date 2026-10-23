# cloud_vs_onprem.py: always-on cluster vs a transient (per-job) cloud cluster, and the time to
# move data to the cloud. ALL PRICES ARE ILLUSTRATIVE - check the provider's price page.
# Measured inputs come from our lab: DistCp 162 MB in 25.5 s (12.2), TestDFSIO aggregate write
# ~210 MB/s on one shared laptop disk (12.3).

# --- 1. compute: a nightly 3-hour job on 20 workers -----------------------------------------
NODE_HOUR = 40.0          # illustrative Rs per worker-hour (on-demand)
SPOT_DISCOUNT = 0.6       # illustrative: spot/preemptible workers 60% cheaper
workers, job_hours = 20, 3
always_on = workers * 24 * 30 * NODE_HOUR
transient = workers * (job_hours + 0.25) * 30 * NODE_HOUR          # +15 min to create and terminate
spot = 4 * (job_hours + 0.25) * 30 * NODE_HOUR + 16 * (job_hours + 0.25) * 30 * NODE_HOUR * (1 - SPOT_DISCOUNT)
print("1. Compute for a month (illustrative prices)")
print(f"   always-on 20 workers      : Rs {always_on:>10,.0f}")
print(f"   transient, 3h15m a night  : Rs {transient:>10,.0f}  ({transient / always_on:.0%} of always-on)")
print(f"   transient, 4 core + 16 spot: Rs {spot:>10,.0f}  ({spot / always_on:.0%})")

# --- 2. storage: 100 TB of data, HDFS x3 replication vs object storage ---------------------
data_tb = 100
DISK_TB_MONTH = 900.0     # illustrative Rs per raw TB-month of cluster disk (server + power + ops)
OBJECT_TB_MONTH = 1700.0  # illustrative Rs per TB-month of object storage (replication included)
hdfs = data_tb * 3 / 0.7 * DISK_TB_MONTH                            # x3 copies, keep disks <= 70% full
obj = data_tb * OBJECT_TB_MONTH
print("2. Storage for 100 TB a month (illustrative prices)")
print(f"   HDFS: {data_tb * 3 / 0.7:.0f} TB of raw disk  : Rs {hdfs:>10,.0f}")
print(f"   object storage, 100 TB  : Rs {obj:>10,.0f}")

# --- 3. moving data: our measured DistCp speed, and a real network link --------------------
lab_mb_s = 162 / 25.5
print("3. Moving 100 TB")
print(f"   at our lab's DistCp speed ({lab_mb_s:.1f} MB/s): {100 * 1024 * 1024 / lab_mb_s / 86400:,.0f} days")
for gbps in [1, 10]:
    mb_s = gbps * 1000 / 8 * 0.7                                      # assume 70% of the link is usable
    print(f"   over a {gbps:>2} Gbps link at 70% use ({mb_s:,.0f} MB/s): {100 * 1024 * 1024 / mb_s / 86400:5.1f} days")
