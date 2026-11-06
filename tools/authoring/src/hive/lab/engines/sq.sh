#!/bin/bash
# sq.sh NAME "SQL" -> spark-sql (Hive 3.1.3 client) output after session start, saved to captures/NAME.txt
/root/lab/engines/sparksql3.sh "$2" 2>&1 | sed -n '/^Hive Session ID/,$p' | grep -vE "^Hive Session ID|^\s+at |\.\.\. [0-9]+ more" > /root/lab/hive/captures/$1.txt
cat /root/lab/hive/captures/$1.txt
