# dfsio_lab.sh: measure what our cluster can write and read (TestDFSIO), the input to any sizing exercise.
# Run inside lab8-namenode-1.
T=$(ls /opt/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-client-jobclient-*-tests.jar)
export HADOOP_CLASSPATH=$T
for files in 1 3 6; do
  for op in write read; do
    yarn org.apache.hadoop.fs.TestDFSIO -libjars $T -$op -nrFiles $files -fileSize 64MB -resFile /tmp/dfsio.txt > /tmp/dfsio.log 2>&1
    echo "== $op, $files file(s) x 64 MB in parallel"
    grep -E "Total MBytes processed|Throughput mb/sec|Average IO rate|Test exec time" /tmp/dfsio.log | sed -E 's/^.*TestDFSIO:[0-9]+ - +/   /'
  done
done
yarn org.apache.hadoop.fs.TestDFSIO -libjars $T -clean > /dev/null 2>&1
