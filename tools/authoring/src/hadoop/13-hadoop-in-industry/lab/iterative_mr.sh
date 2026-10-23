# iterative_mr.sh: the MapReduce way - every pass is a new job that reads HDFS again
cd /tmp/mr; total=$(date +%s)
for k in 1 2 3 4 5; do
  s=$(date +%s); hdfs dfs -rm -r -f -skipTrash /out/iter$k > /dev/null 2>&1
  hadoop jar mr.jar ItemRevenue /user/hadoop/data/orders_x30.csv /out/iter$k > /dev/null 2>&1
  echo "MapReduce pass $k: $(( $(date +%s) - s )) s"
done
echo "MapReduce: 5 passes took $(( $(date +%s) - total )) s"
