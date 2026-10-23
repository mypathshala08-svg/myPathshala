# clean_job_v2.sh: the clean job on 4 compacted files (one per canteen)
hdfs dfs -rm -r -f -skipTrash /capstone/stage/clean_v2
mapred streaming \
  -D mapreduce.job.name=capstone-clean-v2 \
  -D mapreduce.job.reduces=3 \
  -files clean_mapper_v2.py,clean_reducer.py,capstone_raw/menu.csv \
  -input '/capstone/bronze_monthly/orders/college=*' \
  -output /capstone/stage/clean_v2 \
  -mapper clean_mapper_v2.py -reducer clean_reducer.py
hdfs dfs -cat '/capstone/stage/clean/part-*' | sort | md5sum
hdfs dfs -cat '/capstone/stage/clean_v2/part-*' | sort | md5sum
