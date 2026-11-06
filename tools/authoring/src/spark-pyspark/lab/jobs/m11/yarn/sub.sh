#!/bin/bash
# sub.sh MODE  -> spark-submit to YARN
export PYSPARK_PYTHON=python3
cd /tmp; timeout 300 spark-submit --master yarn --deploy-mode $1 --num-executors 2 --executor-cores 1 --executor-memory 768m --driver-memory 768m \
  --conf spark.ui.showConsoleProgress=false --conf spark.yarn.appMasterEnv.PYSPARK_PYTHON=python3 /jobs/m11/yarn_job.py 2>&1
