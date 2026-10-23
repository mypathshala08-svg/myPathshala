# splits_lab.sh: how many input splits (map tasks) does Hadoop make, and where do records start?
cd /tmp/mr
run() {  # run SplitPeek with extra options, print split count and one line per split
  out=/out/peek_$1; shift
  hdfs dfs -rm -r -f -skipTrash $out > /dev/null 2>&1
  hadoop jar mr.jar SplitPeek "$@" $out 2>&1 | grep -o "number of splits:[0-9]*"
  hdfs dfs -cat $out/part-m-* 2>/dev/null
}
echo "== A: canteen_orders.csv (4.7 MB, 1 block)"
run a /user/hadoop/data/canteen_orders.csv
echo "== B: same data stored with 1 MB blocks"
hdfs dfs -D dfs.blocksize=1048576 -put -f canteen_orders.csv /user/hadoop/data/orders_1mb_blocks.csv
hdfs fsck /user/hadoop/data/orders_1mb_blocks.csv -blocks 2>/dev/null | grep "Total blocks"
run b /user/hadoop/data/orders_1mb_blocks.csv
echo "== C: 1 block, but split.maxsize = 1 MB"
run c -D mapreduce.input.fileinputformat.split.maxsize=1048576 /user/hadoop/data/canteen_orders.csv
echo "== D: orders_x30.csv (2 blocks: 128 MB + 6.2 MB)"
run d /user/hadoop/data/orders_x30.csv
echo "== E: orders_x90.csv (4 blocks), then split.minsize = 256 MB"
run e /user/hadoop/data/orders_x90.csv | head -1
run f -D mapreduce.input.fileinputformat.split.minsize=268435456 /user/hadoop/data/orders_x90.csv | head -1
