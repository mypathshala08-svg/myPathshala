# combine_job.sh: the same clean job, but pack the 104 small files into a few splits
hdfs dfs -rm -r -f -skipTrash /capstone/stage/clean_combined
mapred streaming \
  -D mapreduce.job.name=capstone-clean-combined \
  -D mapreduce.job.reduces=3 \
  -D mapreduce.input.fileinputformat.split.maxsize=8388608 \
  -D stream.map.input.ignoreKey=true \
  -files clean_mapper.py,clean_reducer.py,capstone_raw/menu.csv \
  -inputformat org.apache.hadoop.mapred.lib.CombineTextInputFormat \
  -input '/capstone/bronze/orders/college=*' \
  -output /capstone/stage/clean_combined \
  -mapper clean_mapper.py -reducer clean_reducer.py
