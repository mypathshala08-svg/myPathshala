import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *
LAB = os.path.join(HERE, '..', '..', 'lab') + os.sep
CAP = LAB + 'captures' + os.sep
def capf(n):
    return re.sub(r'; Query ID[^\n]*', '', open(CAP + n).read().rstrip())
DAILY = open(LAB + 'capstone/daily_load.hql').read()
def part_of(start, end=None):
    a = DAILY.index(start)
    b = DAILY.index(end) if end else len(DAILY)
    return DAILY[a:b].strip()

def opbox(x, y, label, sub='', tone='card', w=128, h=26):
    o = box(x, y, w, h, tone) + t(x + w / 2, y + (11 if sub else 16), label, 7.2, 'ink', bold=True)
    if sub:
        o += t(x + w / 2, y + 21, sub, 6.4, 'ink2', mono=True)
    return o

MODEL = '''USE tiffingo_dw;
CREATE TABLE dim_restaurant (restaurant_id INT, name STRING, city STRING, cuisine STRING,
  rating DECIMAL(2,1), tags ARRAY<STRING>, onboarded DATE) STORED AS ORC;
CREATE TABLE dim_customer (customer_id INT, name STRING, city STRING, plan STRING,
  valid_from TIMESTAMP, valid_to TIMESTAMP, is_current BOOLEAN)
STORED AS ORC TBLPROPERTIES ('transactional'='true');
CREATE TABLE fact_orders (order_id BIGINT, customer_id INT, restaurant_id INT, order_ts TIMESTAMP,
  amount DECIMAL(10,2), payment STRING, status STRING, updated_at TIMESTAMP, load_date DATE)
PARTITIONED BY (order_date DATE)
STORED AS ORC TBLPROPERTIES ('transactional'='true');
CREATE TABLE fact_deliveries (order_id BIGINT, picked_up_ts TIMESTAMP, delivered_ts TIMESTAMP, rider_id INT)
PARTITIONED BY (load_date DATE) STORED AS ORC;
CREATE TABLE stg_orders (order_id BIGINT, customer_id INT, restaurant_id INT, order_ts TIMESTAMP,
  amount DECIMAL(10,2), payment STRING, status STRING, updated_at TIMESTAMP, order_date DATE,
  raw_line STRING, reject_reason STRING) STORED AS ORC;
CREATE TABLE rejected_orders (raw_line STRING, reject_reason STRING)
PARTITIONED BY (load_date DATE) STORED AS ORC;
CREATE TABLE gold_city_daily (city STRING, orders BIGINT, delivered BIGINT, cancelled BIGINT,
  refunded BIGINT, gmv DECIMAL(14,2), net_revenue DECIMAL(14,2), upi_share DECIMAL(5,2),
  avg_delivery_min DECIMAL(6,1), p90_delivery_min DECIMAL(6,1))
PARTITIONED BY (order_date DATE) STORED AS ORC;
CREATE TABLE etl_audit (load_date DATE, step STRING, row_count BIGINT, run_ts TIMESTAMP) STORED AS ORC;
SHOW TABLES;'''

DIMDATE = '''-- first version
CREATE TABLE dim_date STORED AS ORC AS
SELECT d AS date_key, YEAR(d) AS yr, MONTH(d) AS mon, DAY(d) AS dom,
       DATE_FORMAT(d, 'EEEE') AS day_name, DATE_FORMAT(d, 'u') IN ('6', '7') AS is_weekend
FROM (SELECT DATE_ADD(DATE '2026-01-01', pos) AS d
      FROM (SELECT POSEXPLODE(SPLIT(SPACE(729), ' ')) AS (pos, x)) g) t;

-- the weekend report showed 31 weekdays and 0 weekend days, so we test the expression
SELECT DATE_FORMAT(DATE '2026-10-03', 'u') AS u_pattern, DATE_FORMAT(DATE '2026-10-03', 'E') AS e_pattern,
       DAYOFWEEK(DATE '2026-10-03') AS dayofweek_sat, DAYOFWEEK(DATE '2026-10-04') AS dayofweek_sun;

-- fixed: DAYOFWEEK(d) IN (1, 7) AS is_weekend   (1 = Sunday, 7 = Saturday)
DROP TABLE dim_date;  CREATE TABLE dim_date … ;
SELECT * FROM dim_date WHERE date_key BETWEEN DATE '2026-10-01' AND DATE '2026-10-04';'''

# ---------------------------------------------------------------- story
sc = (box(14, 14, 120, 120, 'card') + t(74, 32, 'raw', 9, bold=True) + t(74, 48, '4 external tables', 7, 'ink2', mono=True) + t(74, 62, '48,871 order rows', 7, 'ink2', mono=True) +
      arrow(136, 74, 176, 74, 'acc', 1.8) +
      box(180, 14, 150, 120, 'blue') + t(255, 32, 'silver', 9, bold=True) +
      ''.join(t(255, 50 + k * 14, s, 7, 'ink2', mono=True) for k, s in enumerate(['stg + quarantine (112)', 'fact_orders 47,553', 'dim_customer SCD 2', 'fact_deliveries', 'dim_restaurant · dim_date']))
      + arrow(332, 74, 372, 74, 'acc', 1.8) +
      box(376, 14, 120, 120, 'green') + t(436, 32, 'gold', 9, bold=True) + t(436, 50, 'gold_city_daily', 7, 'ink2', mono=True) + t(436, 64, '186 rows', 7, 'ink2', mono=True) +
      box(512, 14, 120, 120, 'acc') + t(572, 32, 'CEO answer', 9, bold=True) + t(572, 52, 'Mumbai ₹38.4 L', 7.2, 'ink', mono=True) + t(572, 66, '(raw said ₹42.8 L)', 6.8, 'ink2', mono=True) + t(572, 84, 'gold = fact', 7, 'green', mono=True) + t(572, 98, 're-run safe', 7, 'green', mono=True))
scene_svg = scene('The capstone warehouse: raw tables feed silver tables (staging with quarantine, an ACID fact table upserted with MERGE, an SCD type 2 customer dimension, deliveries and small dimensions), which feed a gold table that answers the CEO: Mumbai earned 38.4 lakh rupees net, not 42.8 lakh.', sc,
                  'One script, run every night, <tspan font-weight="700" class="s-acc">safe to run twice</tspan>.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Build it so that it can run every night without me”</h2>
  <div class="story">
    <p class="narration">Kabir has the design from Lesson 12.1. Now he must turn it into tables and one nightly script, load all of October, and give the CEO numbers that finance can check.</p>

{scene_svg}

A> The design is done. Today you build it. One rule above all: the nightly job must be <b>idempotent</b>. If it fails at step 6 and the on-call engineer simply runs it again, nothing may be counted twice.
K> So no plain <code>INSERT INTO</code> for facts, only <code>INSERT OVERWRITE</code> of a partition or <code>MERGE</code>?
A> Exactly. And after building, we <b>test</b> it: re-run old days, reconcile gold with silver and silver with raw. I promise you, the tests will find bugs.
R> Real bugs, Sir?
A> Real ones. Today’s lab found three: a weekend flag that was always false, a type 2 dimension that broke when an old day was re-run, and a query that hit an engine limit. You will see each one and its fix.
  </div>
</section>
'''

lv = '''
LEVELS> Building the warehouse at three levels
L1> A kitchen that runs every night
      <ul>
        <li>Each night new ingredients arrive (files). The script washes them (types and checks), throws spoiled ones into a labelled bin (quarantine), updates the stock list (MERGE) and plates the dishes (gold).</li>
        <li>If the cook repeats a step by mistake, the dishes must not double: that is <b>idempotence</b>.</li>
      </ul>
L2> The Hive tools used, all from earlier modules
      <ul>
        <li><code>INSERT OVERWRITE … PARTITION</code> for anything that can be recomputed per load (staging, quarantine, deliveries, gold).</li>
        <li><code>MERGE</code> on ACID tables for rows that change over time: <code>fact_orders</code> (upsert) and <code>dim_customer</code> (SCD type 2).</li>
        <li>Window functions to pick the newest version, <code>--hivevar</code> to pass the load date, <code>STACK</code> for the audit rows, <code>EXPLAIN DEPENDENCY</code> to prove pruning.</li>
      </ul>
L3> What makes it production-grade
      <ul>
        <li>Every step is idempotent and proven so by re-running 15 and 3 October: every count and sum unchanged.</li>
        <li>Three-way reconciliation: raw valid orders = fact rows (47,553), fact net revenue = gold net revenue (₹1,53,95,190), rejects = 112.</li>
        <li>Late data handled by rebuilding exactly the order dates a load touched.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>An idempotent, incremental Hive ETL pipeline</h2>
''' + def_block(
    'An <b>ETL pipeline</b> extracts data from sources, transforms it (typing, validation, de-duplication, conforming, modelling) and loads it into target tables. An <b>incremental</b> pipeline processes only one load (here one <code>load_date</code>) per run, and an <b>idempotent</b> pipeline produces the same final state whether a run executes once or several times. In Hive this is achieved by writing recomputable data with <code>INSERT OVERWRITE</code> of the affected partitions and changing data with key-based <code>MERGE</code> on transactional tables, guarded by conditions such as “only newer versions”, and verified by <b>reconciliation</b>: matching counts and totals between layers.',
    'Each night the script handles only that night’s files, puts everything in the right place, and can be run again safely. Then we prove the numbers match from raw to gold.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Idempotent', 'Running twice gives the same result as running once.'),
    ('Upsert', 'Update the row if the key exists, insert it if not: MERGE.'),
    ('Quarantine', 'A table of rejected rows with the reason.'),
    ('Backfill', 'Running the pipeline for past dates, here 31 loads.'),
    ('Reconciliation', 'Checking that counts and sums agree between layers.'),
    ('Point-in-time join', 'Join to the dimension version valid at the event time.'),
    ('hivevar', 'A variable passed to a script: --hivevar load_date=2026-10-05.'),
    ('Touched dates', 'Event dates that received rows in this load.'),
]) + '''

  <h3>The nightly script, step by step</h3>
''' + table(['#', 'Step', 'Hive technique', 'Idempotent because…'], [
    ['0', 'Register today’s folders', '<code>ALTER TABLE … ADD IF NOT EXISTS PARTITION</code>', 'IF NOT EXISTS'],
    ['1', 'Restaurants (SCD 1)', '<code>INSERT OVERWRITE TABLE</code>', 'Full overwrite'],
    ['2', 'Type and validate', '<code>INSERT OVERWRITE</code> stg with <code>CASE … reject_reason</code>', 'Overwrite'],
    ['3', 'Quarantine', '<code>INSERT OVERWRITE … PARTITION (load_date)</code>', 'Overwrite one partition'],
    ['4', 'Orders upsert', '<code>MERGE</code> + <code>ROW_NUMBER()</code>, “only newer”', 'Older or equal versions are ignored'],
    ['5', 'Customers SCD 2', '<code>MERGE</code> with the UNION ALL trick, “only newer”', 'Fixed in Step 7 below'],
    ['6', 'Delivery events', 'Pivot with <code>MAX(IF(…))</code>, overwrite partition', 'Overwrite one partition'],
    ['7', 'Gold', 'Dynamic-partition overwrite of touched <code>order_date</code>s', 'Recomputed from silver'],
    ['8', 'Audit', '<code>INSERT INTO</code> with <code>LATERAL VIEW STACK</code>', 'Append-only by design: shows every run'],
], minw=780) + lv + '''
EXAM> “How do you make a Hive load re-runnable?” Overwrite partitions instead of appending; use MERGE with a business key for changing rows; ignore versions that are not newer; never use plain <code>INSERT INTO</code> on a fact table unless a re-run deletes the previous output first.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Load patterns and when to use each</h2>
''' + table(['Pattern', 'Hive statement', 'Good for', 'Used here'], [
    ['Full refresh', '<code>INSERT OVERWRITE TABLE t SELECT …</code>', 'Small reference data', '<code>dim_restaurant</code>'],
    ['Partition overwrite (static)', '<code>INSERT OVERWRITE … PARTITION (load_date=\'…\')</code>', 'Per-load outputs', 'Quarantine, deliveries'],
    ['Partition overwrite (dynamic)', '<code>INSERT OVERWRITE … PARTITION (order_date) SELECT …, order_date</code>', 'Recomputing a set of event dates', 'Gold'],
    ['Append', '<code>INSERT INTO</code>', 'Logs, audits', '<code>etl_audit</code>'],
    ['Upsert', '<code>MERGE … WHEN MATCHED … WHEN NOT MATCHED</code>', 'Changing facts (status updates)', '<code>fact_orders</code>'],
    ['SCD type 2', '<code>MERGE</code> with a staged UNION ALL', 'History of attributes', '<code>dim_customer</code>'],
    ['Delete + insert', '<code>DELETE</code> then <code>INSERT</code> (ACID)', 'Replacing one key range', 'Not needed'],
], minw=780) + table(['Orchestration option', 'What it is', 'Notes'], [
    ['Shell loop + Beeline', '<code>beeline --hivevar load_date=… -f daily_load.hql</code>', 'What we use; easy to test'],
    ['Apache Airflow', 'Python DAGs with a Hive operator, retries, backfills', 'Most common open-source scheduler today'],
    ['Cloud schedulers', 'Managed Airflow, AWS Step Functions, Dataproc Workflows', 'Lesson 11.2’s platforms'],
    ['Apache Oozie', 'XML workflows on Hadoop', 'Moved to the Apache Attic in 2025; legacy only'],
], minw=640) + '''
WARN> <code>INSERT INTO</code> on a fact table is the most common cause of doubled numbers after a re-run. If you must append, record the load in an audit table and make the job refuse to run twice for the same date.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Building, loading and testing the warehouse</h2>
  <p>All outputs are real (Hive 4.2.1, Tez local mode). The complete script <code>daily_load.hql</code> is in the course’s lab folder; each step shows the part that matters.</p>
''' + stepper([
    ('Step 1 · Silver, gold and control tables',
     code('sql', 'beeline (02_model.hql)', MODEL, capf('l122_tables.txt')),
     'Two tables are <b>ACID</b> because their rows change: <code>fact_orders</code> (refunds) and <code>dim_customer</code> (SCD 2). Everything else is plain ORC and is overwritten partition by partition, which is cheaper and needs no compaction. The fact is partitioned by <code>order_date</code>, the per-load tables by <code>load_date</code>, as decided in Lesson 12.1.'),
    ('Step 2 · A date dimension, and our first bug',
     code('sql', 'beeline', DIMDATE, capf('l122_u.txt') + '\n\n' + capf('l122_dimfix.txt')),
     'The weekend report said “weekday, 31 days”. Testing the expression showed why: in Hive 4, <code>DATE_FORMAT</code> follows Java’s <code>DateTimeFormatter</code>, where <code>u</code> means <b>year</b>, not day of week (older Hive used <code>SimpleDateFormat</code>, where it was the day number). <code>DAYOFWEEK</code> returns 1 for Sunday and 7 for Saturday and does not depend on patterns. Lesson: test every derived column of a dimension with known dates.'),
    ('Step 3 · The nightly script and a 31-day backfill',
     code('bash', 'run_load.sh', 'd=2026-10-01\nwhile [[ "$d" < "2026-11-01" ]]; do\n  beeline -u jdbc:hive2://localhost:10000/tiffingo_dw -n hive --silent=true \\\n          --hivevar load_date=$d -f daily_load.hql > logs/load_$d.log 2>&1\n  echo "$d rc=$?"\n  d=$(date -I -d "$d + 1 day")\ndone', '\n'.join(capf('l122_backfill.txt').split('\n')[:3]) + '\n…\n' + '\n'.join(capf('l122_backfill.txt').split('\n')[-2:]) + '\n\n31 loads, 901 s in total, 29 s per load on average'),
     'One script, one variable. <code>${hivevar:load_date}</code> inside the script is replaced before each statement is compiled. Every load returned exit code 0. About 29 seconds per night is mostly fixed overhead (one Tez DAG per statement in local mode); on a cluster, the same script would scale with the data, not with the number of statements.'),
    ('Step 4 · Type, validate and quarantine',
     code('sql', 'daily_load.hql, steps 2–3', part_of('-- 2. type', '-- 4.') + '\n\n-- after the backfill:\nSELECT reject_reason, COUNT(*) AS n FROM rejected_orders GROUP BY reject_reason ORDER BY n DESC;\nSELECT load_date, reject_reason, raw_line FROM rejected_orders WHERE load_date = DATE \'2026-10-02\';', capf('l122_rejects.txt') + '\n\n' + capf('l122_rejsample.txt')),
     'Each raw row is cast once, and a <code>CASE</code> gives the <b>first</b> rule it breaks. The original line is kept in <code>raw_line</code>, so the source team sees exactly what they sent. The quarantine counts match the profile of Lesson 12.1 exactly (31, 31, 31, 11, 8 = 112). The <code>LEFT JOIN</code> to <code>dim_restaurant</code> is how a foreign-key check is written in Hive, which has no enforced foreign keys.'),
    ('Step 5 · Upsert orders with MERGE',
     code('sql', 'daily_load.hql, step 4 · then checks', part_of('-- 4. upsert', '-- 5.') + "\n\nSELECT COUNT(*) AS orders, COUNT(DISTINCT order_id) AS distinct_ids, SUM(IF(status='DELIVERED',1,0)) AS delivered,\n       SUM(IF(status='CANCELLED',1,0)) AS cancelled, SUM(IF(status='REFUNDED',1,0)) AS refunded FROM fact_orders;\n-- reconcile with raw: distinct order ids that pass every rule\nSELECT COUNT(DISTINCT order_id) AS valid_raw_orders FROM raw_orders o JOIN raw_restaurants r\n  ON CAST(o.restaurant_id AS INT) = r.restaurant_id\nWHERE CAST(o.amount AS DECIMAL(10,2)) > 0 AND CAST(o.order_ts AS TIMESTAMP) IS NOT NULL\n  AND CAST(o.customer_id AS INT) IS NOT NULL;\nSELECT order_id, order_date, status, updated_at, load_date FROM fact_orders WHERE order_id IN (5006782, 5007134);", capf('l122_fact.txt') + '\n\n' + capf('l122_recon.txt') + '\n\n' + capf('l122_one.txt')),
     '<code>ROW_NUMBER()</code> keeps one row per order inside a load (a file contains duplicates, and Hive’s MERGE fails if two source rows match one target row). <code>s.updated_at &gt; t.updated_at</code> makes re-sent rows harmless. Result: 47,553 orders, all unique, exactly the number of valid distinct orders in raw (47,665 − 112). The two orders from Lesson 12.1 are REFUNDED, still in their <code>order_date</code> partition 5 October, with <code>load_date</code> 9 October showing which load changed them.'),
    ('Step 6 · Customers as SCD type 2',
     code('sql', 'daily_load.hql, step 5 (final version)', part_of('-- 5. customers', '-- 6.') + "\n\nSELECT customer_id, city, plan, valid_from, valid_to, is_current FROM dim_customer\nWHERE customer_id IN (1033, 1380) ORDER BY customer_id, valid_from;", capf('l122_scd.txt')),
     'The classic Hive SCD 2 trick: the source is used twice. Rows with <code>join_key</code> = customer id <b>match</b> the current row and close it (<code>valid_to</code>, <code>is_current = false</code>). The same changed rows with <code>join_key</code> = NULL <b>never match</b>, so they are inserted as the new current version. New customers are inserted by the first half. Rohan (1033) now has three versions, each valid until the next begins.'),
    ('Step 7 · The re-run test finds a bug',
     code('sql', 're-run 15 October with the first version of step 5', "-- before: fact_rows, fact_net, dim_rows, gold_net, rejected\n$ run_load.sh 2026-10-15\n\nSELECT customer_id, city, plan, valid_from, valid_to, is_current FROM dim_customer\nWHERE customer_id IN (SELECT customer_id FROM dim_customer GROUP BY customer_id\n                      HAVING SUM(IF(valid_to < valid_from, 1, 0)) > 0)\nORDER BY customer_id, valid_from LIMIT 8;", capf('l122_idem_before.txt') + '\n\n' + capf('l122_idem_after.txt') + '\n\n' + capf('l122_bug.txt')),
     'Orders, gold and quarantine survived the re-run unchanged, but <code>dim_customer</code> grew from 4,166 to 4,171 rows. Customer 1380 moved to Mumbai on 14 October and to Navi Mumbai on 28 October. Re-running 15 October compared the <b>old</b> file with the <b>current</b> version, saw a “change”, closed the newer version with an <b>earlier</b> <code>valid_to</code> and inserted the old Mumbai row as current. The fix is the two <code>updated_at &gt; valid_from</code> conditions you saw in Step 6: only versions newer than what we hold may change the dimension.'),
    ('Step 8 · Rebuild and prove idempotence',
     code('sql', 'rebuild dim_customer with the fixed MERGE, then re-run two old days', "TRUNCATE TABLE dim_customer;   -- then replay step 5 for 1–31 October\nSELECT SUM(IF(valid_to < valid_from, 1, 0)) AS negative_intervals, SUM(IF(is_current, 1, 0)) AS current_rows,\n       COUNT(DISTINCT customer_id) AS customers FROM dim_customer;\n$ run_load.sh 2026-10-15\n$ run_load.sh 2026-10-03\n-- fact_rows, fact_net, dim_rows, gold_net, rejected", capf('l122_bugcheck2.txt') + '\n\n' + capf('l122_rerun2.txt') + '\n\n' + capf('l122_fixed_after.txt')),
     'Replaying one MERGE per day rebuilt the dimension: 4,166 versions, one current row for each of 3,664 customers, no negative intervals. (Raw has 4,167 customer rows: customer 2311 appears twice in the 20 October file and only the newer row counts.) After re-running two old loads, every number is identical. This is what “idempotent” means in practice, and this test belongs in every pipeline’s release checklist.'),
    ('Step 9 · Gold: rebuild only the dates a load touched',
     code('sql', 'daily_load.hql, step 7 · then checks', part_of('-- 7. gold', '-- 8.') + "\n\nSELECT step, row_count FROM etl_audit WHERE load_date = DATE '2026-10-10' ORDER BY step;\nSELECT g.total AS gold_net, f.total AS fact_net, g.total - f.total AS diff\nFROM (SELECT SUM(net_revenue) AS total FROM gold_city_daily) g\nCROSS JOIN (SELECT SUM(amount) AS total FROM fact_orders WHERE status = 'DELIVERED') f;", capf('l122_audit.txt') + '\n\n' + capf('l122_gold_recon.txt')),
     'The 10 October load touched <b>five</b> order dates: today’s orders plus late rows and refunds for earlier days. Only those five gold partitions were rewritten (dynamic partition overwrite replaces only partitions that appear in the output). Because gold is rebuilt from the whole fact and delivery tables, an order whose delivery events arrived a day earlier gets its delivery time now. Gold and fact agree to the paisa: ₹1,53,95,190.'),
    ('Step 10 · An engine limit in the audit step',
     code('sql', 'first version of step 8 · final version', "-- first version: six UNION ALL branches over four tables\nINSERT INTO etl_audit SELECT …, step, n, CURRENT_TIMESTAMP FROM (\n  SELECT 'raw_rows' AS step, COUNT(*) AS n FROM stg_orders\n  UNION ALL SELECT 'rejected', COUNT(*) FROM stg_orders WHERE reject_reason IS NOT NULL\n  UNION ALL … fact_orders … dim_customer … ) a;\n\n" + part_of('-- 8. audit'), capf('l122_counters.txt')),
     'The first audit query failed on day 1: Tez allows 120 counters per job by default, and six branches with their own scans exceeded it. Instead of raising a limit, the query was simplified: one scan of <code>stg_orders</code> computes four numbers, and <code>LATERAL VIEW STACK(4, …)</code> turns those four columns into four rows; the two other tables get one small INSERT each. Fewer stages, same audit, no error.'),
    ('Step 11 · Answers for the CEO',
     code('sql', 'beeline', "SELECT city, SUM(orders) AS orders, SUM(delivered) AS delivered, SUM(refunded) AS refunded,\n       SUM(net_revenue) AS net_revenue, ROUND(AVG(upi_share), 1) AS upi_pct,\n       ROUND(SUM(avg_delivery_min * delivered) / SUM(delivered), 1) AS avg_min, MAX(p90_delivery_min) AS worst_p90\nFROM gold_city_daily WHERE order_date BETWEEN DATE '2026-10-01' AND DATE '2026-10-31'\nGROUP BY city ORDER BY net_revenue DESC;\n\nSELECT IF(d.is_weekend, 'weekend', 'weekday') AS day_type, COUNT(DISTINCT g.order_date) AS days,\n       SUM(g.orders) AS orders, ROUND(SUM(g.orders) / COUNT(DISTINCT g.order_date), 0) AS orders_per_day\nFROM gold_city_daily g JOIN dim_date d ON d.date_key = g.order_date\nGROUP BY IF(d.is_weekend, 'weekend', 'weekday');", capf('l122_gold_city.txt') + '\n\n' + capf('l122_weekend.txt')),
     'Mumbai’s net revenue is <b>₹38,36,320</b>, not the ₹42,77,880 of the old report: ₹4.4 lakh (11.5%) was duplicates, re-sent rows, refunds and cancellations. Bengaluru is almost level with Mumbai; Mumbai and Bengaluru deliveries take about 40 minutes from order to door, other cities about 34. Weekends bring 17% more orders per day (1,711 vs 1,462). The averaged delivery time is weighted by delivered orders; a direct query on the fact table gives the same 40.1 and 39.9.'),
    ('Step 12 · “Do Gold customers spend more?” As of the order',
     code('sql', 'beeline · point-in-time join vs current plan', "SELECT c.plan, COUNT(*) AS orders, ROUND(AVG(f.amount), 2) AS avg_order, SUM(f.amount) AS net_revenue\nFROM fact_orders f\nJOIN dim_customer c ON c.customer_id = f.customer_id\n                   AND f.order_ts >= c.valid_from AND f.order_ts < c.valid_to\nWHERE f.status = 'DELIVERED' GROUP BY c.plan ORDER BY avg_order DESC;\n\n-- the tempting shortcut: today’s plan\n… JOIN dim_customer c ON c.customer_id = f.customer_id AND c.is_current …\n\n-- the mistake: no date condition at all\nSELECT COUNT(*) AS joined_rows FROM fact_orders f JOIN dim_customer c ON c.customer_id = f.customer_id;", capf('l122_pit.txt') + '\n\n-- today’s plan\n' + capf('l122_cur.txt') + '\n\n' + capf('l122_nodate.txt')),
     'Answer for the CEO: Gold customers spend only slightly more per order (₹356 vs ₹353). The point-in-time join credits ₹17.77 lakh to Gold; using today’s plan would claim ₹19.19 lakh, because customers who upgraded later take their old orders with them. Joining without any date condition multiplies rows: 54,418 instead of 47,553. That is the most common SCD 2 bug in interviews and in production.'),
    ('Step 13 · Proof of partition pruning, and a Hive 4 surprise',
     code('sql', 'beeline', "EXPLAIN DEPENDENCY SELECT SUM(amount) FROM fact_orders\nWHERE order_date BETWEEN DATE '2026-10-05' AND DATE '2026-10-06' AND status = 'DELIVERED';\n\nDESCRIBE FORMATTED gold_city_daily;   -- selected lines", capf('l122_explain_fact.txt') + '\n\n' + capf('l122_translated.txt')),
     '<code>EXPLAIN DEPENDENCY</code> lists the inputs a query will read: two partitions out of 31. The second output is a Hive 4 behaviour worth knowing: a “managed” table that is not transactional is <b>translated to an external table</b> with <code>external.table.purge=TRUE</code>. It still behaves like a managed table (DROP deletes the data), but tools that check the table type see EXTERNAL_TABLE. ACID tables stay MANAGED_TABLE.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('2026-10-01 rc=0 27.7s', G), ('2026-10-02 rc=0 28.9s', G), ('…', W), ('2026-10-31 rc=0 29.1s', G), ('31 loads · 901 s', W)], size=7.6),
    term([('bad amount            31', Y), ('missing customer      31', Y), ('unknown restaurant    31', Y), ('bad order_ts          11', Y), ('non-positive amount    8', Y)], size=7.4),
    term([('orders 47553 · distinct 47553', G), ('valid_raw_orders 47553', G), ('5006782 2026-10-05 REFUNDED', W), ('        load_date 2026-10-09', W)], size=7.2),
    term([('re-run 2026-10-15', W), ('dim_rows 4166 → 4171', RD), ('valid_to < valid_from: 5 rows', RD), ('fix: updated_at > valid_from', G)], size=7.4),
    term([('order_dates_touched  5', Y), ('gold_net  15395190.00', G), ('fact_net  15395190.00', G), ('diff      0.00', G)], size=7.6),
    term([('Mumbai  3836320.00 net', G), ('(raw report said 4277880)', RD), ('Gold avg ₹356 · Basic ₹353', W), ('weekend 1711/day · weekday 1462', W)], size=7.2),
]
def pipe(hi):
    names = [('raw', 'load_date', 14, 40), ('stg', 'typed + reason', 130, 40), ('quarantine', '112 rows', 246, 40),
             ('fact_orders', 'MERGE · ACID', 14, 112), ('dim_customer', 'SCD 2 MERGE', 130, 112), ('gold', 'touched dates', 246, 112)]
    o = ''
    for k, (name, sub, x, y) in enumerate(names):
        o += opbox(x, y, name, sub, 'acc' if k == hi else ['card', 'blue', 'amber', 'green', 'violet', 'green'][k], 100, 30)
    o += arrow(116, 55, 128, 55, 'ink3', 1.4) + arrow(232, 55, 244, 55, 'ink3', 1.4) + arrow(180, 72, 64, 110, 'ink3', 1.2) + arrow(116, 127, 128, 127, 'ink3', 1.2, True) + arrow(232, 127, 244, 127, 'ink3', 1.2, True)
    return o
B1 = [
    t(180, 22, 'One script per load_date', 9.4, bold=True) + pipe(0) + cap('--hivevar load_date=…', '', 'blue', y=172, h=34),
    t(180, 22, 'First failed rule wins', 9.4, bold=True) + pipe(2) + cap('Bad rows kept with a reason.', '', 'amber', y=172, h=34),
    t(180, 22, 'Newest version wins', 9.4, bold=True) + pipe(3) + cap('MERGE ignores older or equal rows.', '', 'green', y=172, h=34),
    t(180, 22, 'Old file vs current row', 9.4, bold=True) + pipe(4) + cap('Guard: only newer changes.', '', 'red', y=172, h=34),
    t(180, 22, 'Recompute what changed', 9.4, bold=True) + pipe(5) + cap('Gold = fact, every night.', '', 'green', y=172, h=34),
    t(180, 22, 'Answers from gold', 9.4, bold=True) + pipe(5) + cap('Point-in-time join for plans.', '', 'violet', y=172, h=34),
]
see_caps = ['31 nightly loads, all successful.',
            'Exactly the 112 rows found in Lesson 12.1.',
            'Fact = valid raw orders; refunds updated.',
            'The re-run test caught an SCD 2 bug.',
            'Five dates rebuilt; gold matches fact.',
            'The CEO’s answers, now correct.']
behind_caps = ['The load date selects one raw partition.',
               'CASE gives each row one reject reason.',
               'ROW_NUMBER + MERGE with a newer-only guard.',
               'Old files must not overwrite newer history.',
               'Dynamic overwrite replaces only touched partitions.',
               'Orders join the version valid at order time.']
two = anim_two('The nightly pipeline', 'Raw to gold, safely', 'Real lab outputs', 'Inside the pipeline', see, B1, see_caps, behind_caps)

# ---- scenario 1: failed at step 6
e1 = (t(180, 22, '02:40 · load fails at step 6', 9.4, bold=True) + t(180, 56, 'disk full on the cluster', 8.4, 'ink2') + cap('Steps 0–5 already ran.', '', 'red', y=150, h=34))
e2 = (t(180, 22, 'Fix the disk', 9.4, bold=True) + t(180, 56, 'no manual clean-up of tables', 8.4, 'ink2') + cap('Nothing to undo.', '', 'blue', y=150, h=34))
e3 = (t(180, 22, 'Re-run the whole load', 9.4, bold=True) + t(180, 56, 'run_load.sh 2026-10-16', 8.4, 'ink', mono=True) + cap('Steps 0–5 repeat harmlessly.', '', 'green', y=150, h=34))
e4 = (t(180, 22, 'Audit shows two runs', 9.4, bold=True) + t(180, 56, 'same counts, two run_ts', 8.4, 'ink2') + cap('Evidence for the morning.', '', 'green', y=150, h=34))
e5 = (t(180, 22, '06:00 · dashboard correct', 9.4, 'acc', bold=True) + t(180, 56, 'because every step is idempotent', 8.2, 'ink2') + cap('No one woke the team lead.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'A night-time failure, handled by re-running',
              'Why idempotence matters at 3 a.m. (Typical incident.)',
              'Re-run after failure', 'A load fails half-way; because every step is idempotent the on-call engineer simply re-runs it and the audit shows both runs', [e1, e2, e3, e4, e5],
              ['Failure in the middle.',
               'Fix the cause only.',
               'Run again from the top.',
               'Check the audit.',
               'Correct by morning.'],
              hid='scenario-rerun')

# ---- scenario 2: correction for an old day
b1 = (t(180, 22, 'Source resends 3 October', 9.4, bold=True) + t(180, 56, 'with 40 corrected amounts', 8.4, 'ink2') + cap('A late correction file.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Put it in a new load folder', 9.4, bold=True) + t(180, 56, 'load_date=2026-11-02', 8.4, 'ink', mono=True) + cap('Never edit an old landing file.', '', 'green', y=150, h=34))
b3 = (t(180, 22, 'MERGE updates 40 orders', 9.4, bold=True) + t(180, 56, 'newer updated_at wins', 8.4, 'ink2') + cap('Partition order_date=2026-10-03.', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'Gold rebuilds 3 October', 9.4, bold=True) + t(180, 56, 'touched dates = {10-03, 11-02}', 8.4, 'ink', mono=True) + cap('Only what changed.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Finance sees the fix', 9.4, 'acc', bold=True) + t(180, 56, 'audit row explains the change', 8.2, 'ink2') + cap('Traceable correction.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Correcting an old day without a manual fix',
              'The same pipeline handles corrections. (Illustrative.)',
              'Late correction', 'A corrected file for an old day arrives in a new load; MERGE updates the orders and gold rebuilds only the touched dates', [b1, b2, b3, b4, b5],
              ['Corrections happen.',
               'Treat it as a new load.',
               'Upsert by key.',
               'Recompute touched dates.',
               'Explainable numbers.'],
              hid='scenario-correction')

# ---- scenario 3: scale up
u1 = (t(180, 22, 'TiffinGo grows 200×', 9.4, bold=True) + t(180, 56, '300,000 orders a day', 8.4, 'ink2') + cap('Same design, new settings.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'MERGE scans the whole fact', 9.4, bold=True) + t(180, 56, 'add: AND t.order_date >= cutoff', 8.2, 'ink', mono=True) + cap('Limit the target partitions.', '', 'amber', y=150, h=34))
u3 = (t(180, 22, 'Compaction keeps up', 9.4, bold=True) + t(180, 56, 'automatic initiator + worker', 8.4, 'ink2') + cap('Deltas merged in the background.', '', 'green', y=150, h=34))
u4 = (t(180, 22, 'Gold as Iceberg or MV', 9.4, bold=True) + t(180, 56, 'readable by Trino dashboards', 8.4, 'ink2') + cap('Lessons 9.2 and 11.3.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Airflow instead of a loop', 9.4, 'acc', bold=True) + t(180, 56, 'retries, alerts, backfill UI', 8.2, 'ink2') + cap('Same script inside.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Taking the capstone to production scale',
              'What changes when the data grows. (Typical next steps.)',
              'Scaling up', 'At 200 times the volume, limit MERGE to recent partitions, rely on compaction, serve gold to other engines and schedule with Airflow', [u1, u2, u3, u4, u5],
              ['Bigger data.',
               'Prune the MERGE target.',
               'Let compaction run.',
               'Serve gold widely.',
               'Use a real scheduler.'],
              hid='scenario-scale')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Raw to gold, safely</h2>
  <p>Left: real outputs from the build. Right: what the pipeline does inside.</p>
''' + two + '''
  <p>Three live scenarios follow: a failure at night, a late correction, and scaling up.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>The same pipeline shape in industry</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'orders', 11, 'green', bold=True) + t(60, 58, 'upsert', 7.4, 'ink2'),
    '1. E-commerce and food delivery',
    'Order status changes (placed, delivered, returned, refunded) are merged into one fact row per order every night or every hour.',
    ['Status feed', '*MERGE', 'Order fact']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'banking', 11, 'blue', bold=True) + t(60, 58, 'reconcile', 7.4, 'ink2'),
    '2. Banking and payments',
    'Transactions are reconciled between source, warehouse and ledger every day; differences go to a break report, like our quarantine.',
    ['Core banking', '*recon checks', 'Regulatory report']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'telecom', 11, 'violet', bold=True) + t(60, 58, 'late CDRs', 7.4, 'ink2'),
    '3. Telecom usage',
    'Call and data records arrive hours or days late; daily usage tables are rebuilt for touched dates only.',
    ['CDR files', '*touched dates', 'Usage marts']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'insurance', 9.6, 'acc', bold=True) + t(60, 58, 'SCD 2', 7.4, 'ink2'),
    '4. Insurance and HR',
    'Policy holders’ and employees’ attributes change; claims and payroll are reported with the values valid at the time.',
    ['Master data', '*SCD 2', 'As-of reports']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'retail', 11, 'acc', bold=True) + t(60, 58, 'gold marts', 7.4, 'ink2'),
    '5. Retail dashboards',
    'Store × day gold tables feed BI tools; pre-aggregation keeps dashboards fast for hundreds of users.',
    ['Silver facts', '*gold aggregates', 'BI']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> the problem and the design are in <a href="../01-problem-and-dataset/">Lesson 12.1</a>. This lesson uses window functions (<a href="../../03-querying/06-window-functions/">3.6</a>), dynamic partitions (<a href="../../05-partitioning-and-bucketing/02-dynamic-partitions-and-msck/">5.2</a>) and MERGE with SCD (<a href="../../07-acid-and-iceberg/02-merge-and-scd/">7.2</a>).</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
