# rm.sh fifo|capacity|capacity-preempt|capacity-ulf|capacity-ulf-preempt|fair|drf|default : recreate ONLY the ResourceManager with another scheduler
# (run in the mr-lab folder; HDFS and the NodeManagers keep running)
mode=$1
envs="./config"
case $mode in
  fifo) envs="$envs, ./sched-fifo.env" ;;
  capacity) envs="$envs, ./sched-capacity.env" ;;
  capacity-preempt) envs="$envs, ./sched-capacity.env, ./sched-capacity-preempt.env" ;;
  capacity-ulf) envs="$envs, ./sched-capacity.env, ./sched-capacity-ulf.env" ;;
  capacity-ulf-preempt) envs="$envs, ./sched-capacity.env, ./sched-capacity-ulf.env, ./sched-capacity-preempt.env" ;;
  fair) envs="$envs, ./sched-fair.env" ;;
  drf) envs="$envs, ./sched-drf.env" ;;
  default) ;;
esac
cat > rm-override.yaml <<Y
services:
  resourcemanager:
    env_file: [$envs]
    volumes: [./fair-scheduler.xml:/opt/fair-scheduler.xml:ro]
Y
docker compose -p lab8 -f docker-compose.yaml -f rm-override.yaml up -d resourcemanager 2>&1 | tail -1
until [ "$(docker exec lab8-resourcemanager-1 yarn node -list 2>/dev/null | grep -c RUNNING)" = 3 ]; do sleep 3; done
docker exec lab8-resourcemanager-1 bash -c 'echo "scheduler: $(grep -o "scheduler\.[a-z]*\.[A-Za-z]*Scheduler" /opt/hadoop/etc/hadoop/yarn-site.xml | tail -1)"; mapred queue -list 2>/dev/null | grep -E "Queue Name|Scheduling Info" | paste - - | sed "s/Scheduling Info : //"'
