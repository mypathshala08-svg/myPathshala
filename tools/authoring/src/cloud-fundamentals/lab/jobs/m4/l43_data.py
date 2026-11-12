import duckdb, sqlite3, os, csv
os.chdir('/tmp')
with open('orders.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['order_id','city','amount'])
    for i,(c,a) in enumerate([('Pune',180),('Mumbai',220),('Pune',150),('Delhi',300),('Mumbai',90)],1): w.writerow([i,c,a])
duckdb.sql("COPY (SELECT * FROM (VALUES ('Pune','West',2),('Mumbai','West',3),('Delhi','North',1)) t(city,zone,kitchens)) TO 'cities.parquet' (FORMAT parquet)")
con=sqlite3.connect('crm.db'); con.execute('drop table if exists ratings'); con.execute('create table ratings(order_id int, stars int)'); con.executemany('insert into ratings values (?,?)',[(1,5),(2,4),(3,3),(4,5),(5,2)]); con.commit(); con.close()
print("== 5) data virtualization: three sources, three formats, one SQL query, no copying")
print("  orders.csv (CSV file) · cities.parquet (columnar file) · crm.db (SQLite database)")
d=duckdb.connect(); d.sql("INSTALL sqlite; LOAD sqlite; ATTACH 'crm.db' AS crm (TYPE sqlite)")
print(d.sql("""SELECT c.zone, o.city, count(*) AS orders, sum(o.amount) AS revenue, round(avg(r.stars),1) AS avg_stars
FROM 'orders.csv' o JOIN 'cities.parquet' c USING (city) JOIN crm.ratings r USING (order_id)
GROUP BY ALL ORDER BY revenue DESC"""))
for f in ['orders.csv','cities.parquet','crm.db']: os.remove(f)
