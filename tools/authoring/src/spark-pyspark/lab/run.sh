#!/bin/bash
# run.sh NAME script.py [args]  -> runs locally with quiet logs, saves output (filtered) to captures/NAME.txt
cd /root/lab/spark; n=$1; shift
unset JAVA_TOOL_OPTIONS
export PYSPARK_SUBMIT_ARGS="${PYSPARK_SUBMIT_ARGS:---conf spark.ui.showConsoleProgress=false --driver-java-options -Dlog4j2.configurationFile=/root/lab/spark/log4j2.properties pyspark-shell}"
python3 -W ignore "$@" 2>&1 | grep -vE 'log4j2-defaults|To adjust logging level|NativeCodeLoader|incubator modules|Setting default log level|^\s*$|^\{"ts"' > captures/$n.txt
cat captures/$n.txt
