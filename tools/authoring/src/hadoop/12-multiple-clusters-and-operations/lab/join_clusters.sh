# join_clusters.sh: let the lab8 workers (where DistCp's map tasks run) reach the second cluster.
# Only the workers join: the clusters both use names like "namenode", and a container on two networks
# can answer to the wrong address. Run on your PC.
docker compose -p lab72 start                       # the Lesson 7.2 federation cluster = our "DR" site
for c in worker1 worker2 worker3; do docker network connect lab72_default lab8-$c-1; done
docker exec lab8-worker1-1 getent hosts namenode resourcemanager nn-canteen
docker cp lab8-namenode-1:/tmp/mr/mr.jar /tmp/mr.jar && docker cp /tmp/mr.jar lab8-worker1-1:/tmp/mr.jar
