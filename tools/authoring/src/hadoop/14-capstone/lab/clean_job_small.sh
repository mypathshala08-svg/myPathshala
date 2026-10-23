# clean_job_small.sh: clean_job.sh for a cluster of only 3 DataNodes (keep writing if one dies)
hdfs dfs -rm -r -f -skipTrash /capstone/stage/clean
mapred streaming \
  -D mapreduce.job.name=capstone-clean \
  -D mapreduce.job.reduces=3 \
  -D dfs.client.block.write.replace-datanode-on-failure.policy=NEVER \
  -files clean_mapper.py,clean_reducer.py,capstone_raw/menu.csv \
  -input '/capstone/bronze/orders/college=*' \
  -output /capstone/stage/clean \
  -mapper clean_mapper.py -reducer clean_reducer.py
