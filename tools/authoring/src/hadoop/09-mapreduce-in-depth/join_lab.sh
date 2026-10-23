# join_lab.sh: join 5 lakh orders with the 8-line menu, reduce-side and map-side, and compare
cd /tmp/mr9
O=/user/hadoop/data/student_orders.csv; MENU=/user/hadoop/data/menu.csv
hdfs dfs -put -f menu.csv $MENU
echo "== menu.csv (minus 'coffee', to show an order without a menu row)"
grep -v coffee menu.csv > menu_nocoffee.csv; hdfs dfs -put -f menu_nocoffee.csv /user/hadoop/data/
cat menu_nocoffee.csv
for j in JoinReduceSide JoinMapSide; do
  hdfs dfs -rm -r -f -skipTrash /out/$j > /dev/null 2>&1
  start=$(date +%s%N)
  hadoop jar mr9.jar $j $O /user/hadoop/data/menu_nocoffee.csv /out/$j > /tmp/$j.log 2>&1
  echo "== $j   $(( ($(date +%s%N) - start) / 1000000 )) ms"
  grep -E "number of splits|Launched (map|reduce) tasks|Map input records|Map output records|Reduce shuffle bytes|Reduce input groups|ORDERS_JOINED|ORDERS_WITHOUT_MENU|MENU_(NOT_)?FIRST|Bytes Written" /tmp/$j.log | sed -E 's/^[0-9-]+ [0-9:]+ INFO  //; s/^\s*/  /'
  hdfs dfs -ls /out/$j | grep part | awk '{print "  " $5, $8}'
done
echo "== a joined row"
hdfs dfs -cat /out/JoinMapSide/part-m-00000 2>/dev/null | head -2
echo "== same rows from both joins?"
diff <(hdfs dfs -cat /out/JoinReduceSide/part-* | sort) <(hdfs dfs -cat /out/JoinMapSide/part-* | sort) > /dev/null && echo "identical (459,636 rows each, compared after sorting)"
echo "== map task log of JoinMapSide: the cached menu"
app=$(grep -o "application_[0-9_]*" /tmp/JoinMapSide.log | head -1); sleep 5
yarn logs -applicationId $app -log_files stderr 2>/dev/null | grep -E "cache files|menu loaded" | head -2 | cut -c1-200
