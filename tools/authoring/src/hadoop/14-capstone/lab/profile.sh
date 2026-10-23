# profile.sh: first look at the bronze data (what arrived, how big, how many files and blocks)
hdfs dfs -ls /capstone/bronze/orders
hdfs dfs -ls /capstone/bronze/orders/college=PNL | head -4
hdfs dfs -cat /capstone/bronze/orders/college=KHR/orders_KHR_2026-09-14.csv | head -4
hdfs dfs -cat /capstone/bronze/payments/upi_2026-09-14.jsonl | head -2
hdfs dfs -du -s -h /capstone/bronze/orders/* /capstone/bronze/payments
hdfs fsck /capstone/bronze 2>/dev/null | grep -E "Total (files|blocks|size)|Average block|Minimally|Default replication"
