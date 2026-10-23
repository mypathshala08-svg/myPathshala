# parquet_inside.py: look inside a Parquet file and see row-group skipping (predicate pushdown).
# Needs: pip install pyarrow.  Run next to student_orders.csv (from Module 9's make_student_orders.py).
import pyarrow as pa, pyarrow.csv as csv, pyarrow.parquet as pq, pyarrow.compute as pc

names = ["order_id", "student", "time", "item", "amount"]
t = csv.read_csv("student_orders.csv", read_options=csv.ReadOptions(column_names=names))
pq.write_table(t, "orders.parquet", row_group_size=50_000, compression="snappy")
pq.write_table(t.sort_by("student"), "orders_sorted.parquet", row_group_size=50_000, compression="snappy")

md = pq.ParquetFile("orders.parquet").metadata
print(f"rows {md.num_rows:,}  row groups {md.num_row_groups}  created by: {md.created_by}")
rg = md.row_group(0)
print("row group 0, per column chunk:")
for i in range(rg.num_columns):
    c = rg.column(i)
    print(f"  {c.path_in_schema:9} {c.compression:7} {c.total_compressed_size:>8,} bytes  "
          f"encodings {','.join(e for e in c.encodings)}  min={c.statistics.min} max={c.statistics.max}")

def groups_to_read(path, student):
    f = pq.ParquetFile(path)
    hits = []
    for i in range(f.metadata.num_row_groups):
        s = f.metadata.row_group(i).column(1).statistics          # column 1 = student
        if s.min <= student <= s.max:                              # the footer says it MIGHT be here
            hits.append(i)
    return hits, f.metadata.num_row_groups

for path in ["orders.parquet", "orders_sorted.parquet"]:
    hits, total = groups_to_read(path, "S1413")
    rows = pq.read_table(path, filters=[("student", "=", "S1413")]).num_rows
    print(f"{path:22} student = 'S1413': must read {len(hits)} of {total} row groups {hits}  -> {rows} rows")
