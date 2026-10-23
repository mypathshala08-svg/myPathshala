# clean_job.sh: bronze -> cleaned text with Hadoop Streaming (3 reducers)
hdfs dfs -rm -r -f -skipTrash /capstone/stage/clean
mapred streaming \
  -D mapreduce.job.name=capstone-clean \
  -D mapreduce.job.reduces=3 \
  -files clean_mapper.py,clean_reducer.py,capstone_raw/menu.csv \
  -input '/capstone/bronze/orders/college=*' \
  -output /capstone/stage/clean \
  -mapper clean_mapper.py -reducer clean_reducer.py
