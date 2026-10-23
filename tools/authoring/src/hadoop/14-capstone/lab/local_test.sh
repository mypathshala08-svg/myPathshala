# run mapper | sort | reducer on your PC first (no cluster needed)
for f in capstone_raw/orders/*/*.csv; do mapreduce_map_input_file=$f python3 clean_mapper.py < $f; done 2>local_mapcnt \
 | LC_ALL=C sort -t$'\t' -k1,1 | (cd capstone_raw && python3 ../clean_reducer.py) 2>local_redcnt > local_clean_local.tsv
sort local_mapcnt local_redcnt | awk -F, '{s[$2]+=$3} END {for (k in s) print k, s[k]}' | sort
wc -l local_clean_local.tsv
