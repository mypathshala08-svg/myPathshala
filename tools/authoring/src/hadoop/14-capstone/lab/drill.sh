# drill.sh: run the clean job and break worker2 while it runs (run from the host, not a container)
docker exec -w /tmp/capstone lab8-namenode-1 bash clean_job.sh > tx_drill.txt 2>&1 &
sleep 75
docker exec lab8-worker2-1 bash -c 'pkill -9 -f "[Y]arnChild"; hdfs --daemon stop datanode'   # kill running tasks + DataNode
wait
docker exec lab8-worker2-1 hdfs --daemon start datanode
