# Lesson 5.2 — three ways to keep SaaS tenants' data apart (SQLite stands in for any database)
import sqlite3, os
os.chdir('/tmp'); [os.remove(f) for f in os.listdir('.') if f.startswith('t_') and f.endswith('.db')]
rows = [('annapurna', 'order 1', 250), ('annapurna', 'order 2', 180), ('dabbawala', 'order 1', 300), ('ghar-ka-khana', 'order 1', 120)]
print("== 1) pool model: one shared table, every row tagged with tenant_id")
db = sqlite3.connect(':memory:'); db.execute('create table orders(tenant_id, item, amount)'); db.executemany('insert into orders values (?,?,?)', rows)
print("  bug — a query that forgot the tenant filter returns:", db.execute('select tenant_id, item from orders').fetchall())
print("  correct — tenant 'annapurna' only:", db.execute('select item, amount from orders where tenant_id=?', ('annapurna',)).fetchall())
db.execute("create view v_annapurna as select item, amount from orders where tenant_id='annapurna'")
print("  safer — a per-tenant view the app is forced to use:", db.execute('select * from v_annapurna').fetchall())
print("== 2) bridge model: one database, one schema (here: attached DB) per tenant")
db2 = sqlite3.connect(':memory:')
for t in ['annapurna', 'dabbawala']:
    db2.execute(f"attach 't_{t}.db' as {t.replace('-', '_')}"); db2.execute(f"create table {t}.orders(item, amount)")
db2.execute("insert into annapurna.orders values ('order 1', 250)"); db2.commit()
print("  schemas:", [r[1] for r in db2.execute('pragma database_list')][1:], " annapurna.orders:", db2.execute('select * from annapurna.orders').fetchall(), " dabbawala.orders:", db2.execute('select * from dabbawala.orders').fetchall())
print("== 3) silo model: a separate database file per tenant")
for t in ['annapurna', 'dabbawala', 'ghar-ka-khana']:
    c = sqlite3.connect(f't_{t}_silo.db'); c.execute('create table if not exists orders(item, amount)'); c.commit(); c.close()
print("  files:", sorted(f for f in os.listdir('.') if f.endswith('_silo.db')))
[os.remove(f) for f in os.listdir('.') if f.startswith('t_') and f.endswith('.db')]
