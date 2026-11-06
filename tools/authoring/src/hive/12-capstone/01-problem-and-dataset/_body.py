import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *
CAP = os.path.join(HERE, '..', '..', 'lab', 'captures') + os.sep
def capf(n):
    return re.sub(r'; Query ID[^\n]*', '', open(CAP + n).read().rstrip())

def opbox(x, y, label, sub='', tone='card', w=128, h=26):
    o = box(x, y, w, h, tone) + t(x + w / 2, y + (11 if sub else 16), label, 7.2, 'ink', bold=True)
    if sub:
        o += t(x + w / 2, y + 21, sub, 6.4, 'ink2', mono=True)
    return o

RAW_DDL = '''CREATE DATABASE IF NOT EXISTS tiffingo_dw COMMENT 'TiffinGo capstone warehouse';
USE tiffingo_dw;
-- raw layer: every column is STRING, so no row is ever lost at read time
CREATE EXTERNAL TABLE raw_orders (
  order_id STRING, customer_id STRING, restaurant_id STRING, order_ts STRING,
  amount STRING, payment STRING, status STRING, updated_at STRING)
PARTITIONED BY (load_date STRING)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION 'file:///data/capstone/landing/orders'
TBLPROPERTIES ('skip.header.line.count'='1');
-- raw_customers: same pattern (CSV, header, load_date folders)
CREATE EXTERNAL TABLE raw_deliveries (order_id BIGINT, event STRING, event_ts STRING, rider_id INT)
PARTITIONED BY (load_date STRING) STORED AS JSONFILE
LOCATION 'file:///data/capstone/landing/deliveries';
CREATE EXTERNAL TABLE raw_restaurants (restaurant_id INT, name STRING, city STRING,
  cuisine STRING, rating DECIMAL(2,1), tags ARRAY<STRING>, onboarded STRING)
STORED AS JSONFILE LOCATION 'file:///data/capstone/landing/restaurants';
MSCK REPAIR TABLE raw_orders;      -- registers the 31 load_date folders
MSCK REPAIR TABLE raw_customers;
MSCK REPAIR TABLE raw_deliveries;
SELECT COUNT(DISTINCT load_date) AS order_loads, MIN(load_date) AS first_load, MAX(load_date) AS last_load
FROM raw_orders;'''

# ---------------------------------------------------------------- story
sc = (opbox(14, 16, 'CEO’s question', 'which city is really growing?', 'blue', 160, 30) +
      opbox(14, 58, 'Old report', 'raw files, summed directly', 'amber', 160, 30) +
      opbox(14, 100, 'Mumbai “₹42.8 lakh”', 'duplicates, refunds counted', 'red', 160, 30) +
      arrow(178, 73, 236, 73, 'acc', 1.8) +
      box(240, 34, 150, 78, 'green') + t(315, 56, 'Capstone: a real', 8.6, bold=True) + t(315, 70, 'Hive warehouse', 8.6, bold=True) + t(315, 90, 'raw → silver → gold', 7.4, 'ink2', mono=True) +
      box(410, 10, 222, 132, 'card') + t(521, 28, 'What October’s files contain', 8.6, bold=True) +
      ''.join(t(422, 48 + k * 15, s, 7.1, c, anchor='start', mono=True) for k, (s, c) in enumerate([
          ('48,871 order rows, 47,665 orders', 'ink'), ('546 duplicate and resent rows', 'amber'), ('660 orders change later (refunds)', 'amber'),
          ('2,078 rows for an earlier day', 'amber'), ('112 broken rows', 'red'), ('469 customers changed city/plan', 'violet'), ('88,462 delivery events', 'ink')])))
scene_svg = scene('TiffinGo’s CEO asks which city is really growing. The old report summed raw files directly and was wrong. The capstone builds a proper Hive warehouse from October’s 94 landing files, which contain duplicates, late rows, refunds, broken rows and customer changes.', sc,
                  'Before writing one table, <tspan font-weight="700" class="s-acc">find out what the data really looks like</tspan>.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Why does every report give a different number?”</h2>
  <div class="story">
    <p class="narration">It is the first Monday of November. TiffinGo’s CEO wants a one-page answer: orders, revenue and delivery speed per city for October, and whether Gold-plan customers really spend more. Last month an analyst summed the raw files and Mumbai came out at ₹42.8 lakh. Finance said it was wrong. Arjun Sir turns this into the course capstone.</p>

{scene_svg}

A> Kabir, for three lessons you are the data engineer. Your job: build TiffinGo’s Hive warehouse for October and answer the CEO. Today we do not write a single production table. Today we <b>understand the problem and the data</b>.
K> Sir, the data is just CSV and JSON files. Why not load it and run GROUP BY?
A> That is exactly what the analyst did. Let us see what is inside those files first: duplicates, resends, late rows, refunds, broken lines, customers who move city. Every one of them changes the CEO’s number.
R> So we profile the data with Hive, and the problems we find decide the design?
A> Exactly. Requirements and data profiling first, design second, code third. Every output today is real, from our Hive 4.2.1 lab.
  </div>
</section>
'''

lv = '''
LEVELS> The capstone at three levels
L1> A kitchen before service
      <ul>
        <li>A good cook first checks the delivery: what arrived, what is spoiled, what is missing. That is <b>profiling</b>.</li>
        <li>Then the cook plans the shelves: raw items, washed and cut items, ready dishes. Those are the <b>raw, silver and gold</b> layers.</li>
        <li>Only then does the cooking (the code) start, in Lesson 12.2.</li>
      </ul>
L2> What a data engineer delivers in this lesson
      <ul>
        <li>A <b>requirements list</b>: the questions (KPIs) and how fresh, correct and fast the answers must be.</li>
        <li>A <b>source inventory</b> and a <b>profile</b> of each source: rows, keys, duplicates, late data, bad values, changes over time.</li>
        <li>A <b>design</b>: layers, star schema with the grain of each fact, partitioning, file formats, slowly changing dimensions and data-quality rules.</li>
      </ul>
L3> Decisions the profile forced on us
      <ul>
        <li>1,206 extra rows (546 copies + 660 refund versions) → the fact table needs a <b>key and an upsert (MERGE)</b>, not an append.</li>
        <li>2,078 rows for older dates → load by <code>load_date</code>, partition the fact by <code>order_date</code>, and <b>rebuild every date a load touches</b>.</li>
        <li>469 customers changed city or plan → <code>dim_customer</code> is <b>SCD type 2</b>, joined “as of” the order time.</li>
        <li>112 broken rows → a <b>quarantine</b> table with a reason, never silent drops.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>A data warehouse capstone: requirements, profiling and design</h2>
''' + def_block(
    'A <b>data warehouse</b> is a subject-oriented, integrated, time-variant and non-volatile collection of data that supports analysis and decision making. In a Hive warehouse, source files land in <b>raw</b> (external) tables, are cleaned, typed and de-duplicated into <b>silver</b> tables, and are modelled as a <b>star schema</b>: <b>fact tables</b> holding measurable events at a declared <b>grain</b>, surrounded by <b>dimension tables</b> holding descriptive context, some kept as <b>slowly changing dimensions</b>. Aggregated <b>gold</b> tables answer the business questions. <b>Data profiling</b> is the systematic measurement of the source data (volumes, keys, duplicates, nulls, invalid values, late and changing records) that the design must handle.',
    'Before building, measure the data: what is duplicated, late, broken or changing. Then design layers (raw → silver → gold), a star schema (facts + dimensions) and rules so that the final numbers are right.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('KPI', 'Key performance indicator: a number the business tracks, e.g. net revenue per city.'),
    ('Grain', 'What one row of a fact table means. Here: one order, latest version.'),
    ('Fact table', 'Measurable events (orders, deliveries) with keys to dimensions.'),
    ('Dimension', 'Descriptive context: customer, restaurant, date.'),
    ('SCD type 2', 'A dimension that keeps history: a new row per change, with valid_from / valid_to.'),
    ('Landing zone', 'Where source systems drop files, untouched.'),
    ('Late-arriving data', 'Rows that reach us in a later load than the day they happened.'),
    ('Idempotent load', 'A load you can re-run with the same result, no double counting.'),
]) + '''

  <h3>From requirement to design decision</h3>
''' + table(['CEO / team asked for', 'What the profile showed', 'Design decision'], [
    ['Orders and revenue per city per day', 'Duplicates and resent rows (546)', 'Fact grain = one order; MERGE on <code>order_id</code>'],
    ['Net revenue (refunds excluded)', '660 orders become REFUNDED 1–4 days later', 'Keep the newest version by <code>updated_at</code>'],
    ['Correct daily numbers even after late rows', '2,078 rows describe an earlier day', 'Partition fact by <code>order_date</code>; rebuild touched dates'],
    ['Revenue by plan at the time of order', '469 customers changed city or plan', '<code>dim_customer</code> as SCD type 2'],
    ['Delivery speed per city', 'Events in JSON; 998 orders’ events arrive before the order row', 'Separate delivery fact; LEFT JOIN, recompute later'],
    ['Trust in the numbers', '112 broken rows of five kinds', 'Quarantine with reason + audit table'],
], minw=760) + lv + '''
EXAM> Bill Inmon’s classic definition of a data warehouse has four words: <b>subject-oriented, integrated, time-variant, non-volatile</b>. In a star schema, always state the <b>grain</b> of a fact table first (“one row per order”), then its measures and its dimension keys.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Layers, tables and change types you choose from</h2>
''' + table(['Layer', 'Also called', 'Hive table type', 'In our capstone'], [
    ['Raw', 'Bronze, landing, staging-in', 'External, TEXTFILE/JSON, all STRING, partitioned by load date', '<code>raw_orders</code>, <code>raw_customers</code>, <code>raw_deliveries</code>, <code>raw_restaurants</code>'],
    ['Silver', 'Cleansed, conformed, core', 'Managed ORC; ACID where rows change', '<code>stg_orders</code>, <code>rejected_orders</code>, <code>fact_orders</code> (ACID), <code>fact_deliveries</code>, dimensions'],
    ['Gold', 'Mart, presentation, serving', 'Managed ORC aggregates, views or materialized views', '<code>gold_city_daily</code>'],
    ['Control', 'Audit, metadata', 'Small managed tables', '<code>etl_audit</code>'],
], minw=760) + table(['Fact table type', 'One row is…', 'Example'], [
    ['Transaction', 'One event', '<code>fact_orders</code>: one order (latest version)'],
    ['Periodic snapshot', 'State at a regular time', 'Wallet balance per customer per day'],
    ['Accumulating snapshot', 'One process, updated as it moves', 'Order with placed / picked up / delivered timestamps'],
    ['Factless', 'An event with no measure', 'A customer opened the app'],
], minw=620) + table(['SCD type', 'What happens on change', 'When to use'], [
    ['Type 0', 'Never change', 'Date of birth, sign-up date'],
    ['Type 1', 'Overwrite, no history', 'Fixing a typo; our <code>dim_restaurant</code>'],
    ['Type 2', 'New row; old row closed with <code>valid_to</code>', 'City and plan of a customer: <code>dim_customer</code>'],
    ['Type 3', 'Extra column for the previous value', '“previous_plan” when only one step back matters'],
    ['Type 4', 'Current table + separate history table', 'Very fast-changing attributes'],
    ['Type 6', '1 + 2 + 3 combined', 'Current value on every historic row'],
], minw=620) + table(['Load style', 'Meaning', 'Our sources'], [
    ['Full snapshot', 'Every row every time', 'Restaurants (150 rows), customers on day 1'],
    ['Incremental', 'Only new rows since the last load', 'Orders and delivery events per day'],
    ['CDC (change data capture)', 'Inserts and changes with a change timestamp', 'Customers after day 1; order status updates'],
], minw=620) + '''
TIP> Medallion names (bronze, silver, gold) come from lakehouse vendors; Kimball’s names (staging, presentation) are older. Interviewers accept either. What matters is that you can say what each layer guarantees.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Profiling October’s landing files in Hive</h2>
  <p>The generator <code>make_capstone.py</code> (in the course’s lab folder) wrote 31 nightly drops the way a source system would. Every output below is real, from Hive 4.2.1 with Beeline.</p>
''' + stepper([
    ('Step 1 · Look at the landing zone',
     code('bash', 'terminal', 'find landing -type f | sort | head -6\nfind landing -type f | wc -l\ndu -sh landing/*', capf('l121_tree.txt').split('\n', 1)[1].replace('$ find landing -type f | wc -l\n', '').replace('$ du -sh landing/*\n', '')),
     'One folder per source and per nightly load, named <code>load_date=YYYY-MM-DD</code>. That naming is deliberate: Hive can register each folder as a partition. 31 order files, 31 customer files, 31 event files and one restaurant file: 94 in total, 12.6 MB. Small for Hive, but every real-world problem is inside.'),
    ('Step 2 · Raw tables over the files',
     code('sql', 'beeline', RAW_DDL, capf('l121_nparts.txt')),
     'Raw tables are <b>external</b> (dropping them never deletes source files) and every CSV column is <code>STRING</code>. If <code>amount</code> were DECIMAL, the row with <code>NA</code> would silently become NULL and we would not know what the source sent. <code>MSCK REPAIR</code> found the 31 folders and added them as partitions.'),
    ('Step 3 · Volumes per source and per load',
     code('sql', 'beeline', "SELECT 'raw_orders' AS tbl, COUNT(*) AS n FROM raw_orders\nUNION ALL SELECT 'raw_customers', COUNT(*) FROM raw_customers\nUNION ALL SELECT 'raw_deliveries', COUNT(*) FROM raw_deliveries\nUNION ALL SELECT 'raw_restaurants', COUNT(*) FROM raw_restaurants;\n\nSELECT load_date, COUNT(*) AS n FROM raw_orders\nWHERE load_date BETWEEN '2026-10-01' AND '2026-10-07'\nGROUP BY load_date ORDER BY load_date;", capf('l121_counts.txt') + '\n\n' + capf('l121_perload.txt')),
     'About 1,500 order rows per night, more on 3 and 4 October (a Saturday and Sunday). The header line of every file was skipped by <code>skip.header.line.count</code>. These counts become the first data-quality check: a nightly load with 0 or 15,000 rows is an alarm, not a load. (<code>UNION ALL</code> does not promise row order.)'),
    ('Step 4 · Is order_id really a key?',
     code('sql', 'beeline', "SELECT COUNT(*) AS raw_rows, COUNT(DISTINCT order_id) AS distinct_orders,\n       COUNT(DISTINCT order_id, status, updated_at) AS distinct_versions\nFROM raw_orders;\n\nSELECT n_versions, COUNT(*) AS orders FROM (\n  SELECT order_id, COUNT(DISTINCT CONCAT(status, '|', updated_at)) AS n_versions\n  FROM raw_orders GROUP BY order_id) v\nGROUP BY n_versions ORDER BY n_versions;", capf('l121_dups.txt') + '\n\n' + capf('l121_versions.txt')),
     '48,871 rows but only 47,665 orders. 48,871 − 48,325 = <b>546 rows are exact copies</b> (duplicates in a file plus rows the source re-sent the next night). And 660 orders have <b>two versions</b>: same <code>order_id</code>, different status and <code>updated_at</code>. So <code>order_id</code> is the business key, but the raw table is a log of versions. Summing it double-counts.'),
    ('Step 5 · What the second version is',
     code('sql', 'beeline', "SELECT load_date, order_id, status, updated_at FROM raw_orders\nWHERE order_id IN (SELECT order_id FROM raw_orders\n                   WHERE status = 'REFUNDED' AND load_date = '2026-10-09')\nORDER BY order_id, updated_at LIMIT 4;", capf('l121_onehist.txt')),
     'Order 5006782 was DELIVERED on 5 October and REFUNDED on 9 October, and the refund arrived in the 9 October file. The newest version (largest <code>updated_at</code>) is the truth. This is change data capture in its simplest form, and it means the fact table must be <b>updated</b>, not just appended: a job for ACID tables and <code>MERGE</code> (Module 7).'),
    ('Step 6 · Late rows: when did it happen versus when did it arrive?',
     code('sql', 'beeline', "SELECT CASE WHEN TO_DATE(order_ts) = load_date THEN 'same day'\n            WHEN TO_DATE(order_ts) < load_date THEN 'older order'\n            WHEN order_ts IS NULL OR TO_DATE(order_ts) IS NULL THEN 'bad timestamp' END AS arrival,\n       status, COUNT(*) AS n\nFROM raw_orders\nGROUP BY CASE WHEN TO_DATE(order_ts) = load_date THEN 'same day'\n              WHEN TO_DATE(order_ts) < load_date THEN 'older order'\n              WHEN order_ts IS NULL OR TO_DATE(order_ts) IS NULL THEN 'bad timestamp' END, status\nORDER BY arrival, status;", capf('l121_late.txt')),
     '2,078 rows describe orders from an earlier day: 663 are refund versions, the rest are orders placed late at night or delayed by the source, plus re-sent rows. So a load on 10 October changes the numbers of 9 October. Two dates matter for every row: <code>load_date</code> (when we received it, for raw partitions and re-runs) and <code>order_date</code> (when it happened, for the fact table and every report).'),
    ('Step 7 · Broken rows, measured per rule',
     code('sql', 'beeline', "SELECT SUM(IF(CAST(o.amount AS DECIMAL(10,2)) IS NULL, 1, 0)) AS bad_amount,\n       SUM(IF(CAST(o.amount AS DECIMAL(10,2)) <= 0, 1, 0))  AS non_positive,\n       SUM(IF(CAST(o.order_ts AS TIMESTAMP) IS NULL, 1, 0)) AS bad_ts,\n       SUM(IF(o.customer_id = '' OR o.customer_id IS NULL, 1, 0)) AS no_customer,\n       SUM(IF(r.restaurant_id IS NULL, 1, 0)) AS unknown_restaurant\nFROM raw_orders o\nLEFT JOIN raw_restaurants r ON CAST(o.restaurant_id AS INT) = r.restaurant_id;\n\nSELECT load_date, order_id, customer_id, restaurant_id, order_ts, amount FROM raw_orders\nWHERE load_date = '2026-10-01' AND (CAST(amount AS DECIMAL(10,2)) IS NULL\n   OR CAST(amount AS DECIMAL(10,2)) <= 0 OR CAST(order_ts AS TIMESTAMP) IS NULL\n   OR customer_id = '' OR restaurant_id = '999');", capf('l121_quality.txt') + '\n\n' + capf('l121_badrows.txt')),
     'Five kinds of broken rows: <code>NA</code> amounts, negative amounts, a date in <code>dd/MM/yyyy</code> format, an empty customer and restaurant 999, which does not exist. <code>CAST</code> returns NULL instead of failing, which is useful for measuring and dangerous for loading. Over the month that is 31 + 8 + 11 + 31 + 31 = <b>112 broken rows</b>, each failing exactly one rule (a negative amount is a valid number, so it is not in <code>bad_amount</code>). Each rule becomes a <b>reject reason</b> in Lesson 12.2, and broken rows go to a quarantine table instead of disappearing.'),
    ('Step 8 · Customers change: the case for SCD type 2',
     code('sql', 'beeline', "SELECT versions, COUNT(*) AS customers FROM (\n  SELECT customer_id, COUNT(*) AS versions FROM raw_customers GROUP BY customer_id) x\nGROUP BY versions ORDER BY versions;\n\nSELECT customer_id, name, city, plan, updated_at, load_date FROM raw_customers\nWHERE customer_id IN (SELECT customer_id FROM raw_customers\n                      GROUP BY customer_id HAVING COUNT(*) >= 3)\nORDER BY customer_id, updated_at LIMIT 6;", capf('l121_custver.txt') + '\n\n' + capf('l121_cust.txt')),
     'Day 1 is a full snapshot of 3,000 customers; after that each file holds only new sign-ups and changes. 469 customers have 2–4 versions. Rohan Gupta moved from Bengaluru to Navi Mumbai on 11 October and upgraded to Silver on 25 October. If we overwrite (type 1), his early-October orders would be credited to Navi Mumbai and to Silver. The CEO’s “do Gold customers spend more?” needs the plan <b>at the time of each order</b>: SCD type 2.'),
    ('Step 9 · Delivery events and the order they belong to',
     code('sql', 'beeline', "SELECT event, COUNT(*) AS n, COUNT(DISTINCT order_id) AS orders,\n       MIN(event_ts) AS first_ts, MAX(event_ts) AS last_ts\nFROM raw_deliveries GROUP BY event;\n\nSELECT COUNT(DISTINCT d.order_id) AS delivered_without_order_same_load\nFROM raw_deliveries d\nLEFT JOIN raw_orders o ON CAST(o.order_id AS BIGINT) = d.order_id AND o.load_date = d.load_date\nWHERE d.event = 'DELIVERED' AND o.order_id IS NULL;", capf('l121_events.txt') + '\n\n' + capf('l121_orphan_ev.txt')),
     'Two events per delivered order, read straight from JSON by <code>STORED AS JSONFILE</code>. One delivery finished at 00:13 on 1 November: a day boundary inside one order. And for 998 orders the rider events arrived in a load <b>before</b> the order row did. A gold table built only from today’s orders would miss their delivery time, so gold must be rebuilt for every order date a load touches, joining the full delivery table.'),
    ('Step 10 · Why the old report was wrong',
     code('sql', 'beeline', "SELECT r.city, COUNT(*) AS orders,\n       ROUND(SUM(CAST(o.amount AS DECIMAL(10,2))), 0) AS amount\nFROM raw_orders o JOIN raw_restaurants r\n  ON CAST(o.restaurant_id AS INT) = r.restaurant_id\nGROUP BY r.city ORDER BY orders DESC;", capf('l121_city.txt')),
     'This is the analyst’s query. Mumbai shows ₹42,77,880 from 12,119 “orders”, but the total includes duplicate rows, re-sent rows, both versions of refunded orders and cancelled orders, while a broken <code>NA</code> amount simply vanished from the sum. Every one of these errors is invisible in the result. In Lesson 12.2 the same question, asked of the gold table, gives the correct and lower number.'),
]) + '''
  <h3 id="design">The design we take into Lesson 12.2</h3>
''' + table(['Table', 'Layer', 'Grain / content', 'Storage', 'Partition', 'Load rule'], [
    ['<code>raw_*</code> (4)', 'Raw', 'Exactly what the source sent', 'External text / JSON', '<code>load_date</code>', 'Register folder'],
    ['<code>stg_orders</code>', 'Silver', 'One typed row per raw row of one load, with <code>reject_reason</code>', 'ORC', '—', 'Overwrite per load'],
    ['<code>rejected_orders</code>', 'Silver', 'Broken raw lines + reason', 'ORC', '<code>load_date</code>', 'Overwrite partition'],
    ['<code>fact_orders</code>', 'Silver', 'One row per order, latest version', 'ORC, ACID', '<code>order_date</code>', 'MERGE (upsert)'],
    ['<code>fact_deliveries</code>', 'Silver', 'One row per delivered order', 'ORC', '<code>load_date</code>', 'Overwrite partition'],
    ['<code>dim_customer</code>', 'Silver', 'One row per customer version', 'ORC, ACID', '—', 'SCD 2 MERGE'],
    ['<code>dim_restaurant</code>', 'Silver', 'One row per restaurant', 'ORC', '—', 'Overwrite (SCD 1)'],
    ['<code>dim_date</code>', 'Silver', 'One row per calendar day, 2026–2027', 'ORC', '—', 'Generate once'],
    ['<code>gold_city_daily</code>', 'Gold', 'One row per city per order date', 'ORC', '<code>order_date</code>', 'Overwrite touched dates'],
    ['<code>etl_audit</code>', 'Control', 'Counts per load and step', 'ORC', '—', 'Append'],
], minw=880) + '''
  <p>Why these choices: the fact is partitioned by <code>order_date</code> because every report filters by it, and a month gives 31 partitions of about 1,500 rows (in production you might partition by month at this size; Lesson 5.4). No bucketing: the largest table has under 50,000 rows. ORC because Hive ACID requires it and it compresses well (Module 6). Plain ORC, not ACID, wherever a load can simply overwrite a partition, because overwrite is cheaper and needs no compaction.</p>
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('find landing -type f | wc -l', W), ('94', G), ('CREATE EXTERNAL TABLE raw_orders (… STRING)', W), ('MSCK REPAIR TABLE raw_orders', W), ('order_loads 31', G)], size=7.0),
    term([('raw_rows           48871', W), ('distinct_orders    47665', Y), ('distinct_versions  48325', Y), ('n_versions 2 → 660 orders', Y)], size=7.6),
    term([('older order  DELIVERED  1294', Y), ('older order  REFUNDED    663', Y), ('older order  CANCELLED   121', Y), ('bad timestamp            11', RD)], size=7.6),
    term([('bad_amount 31 · non_positive 8', RD), ('bad_ts 11 · no_customer 31', RD), ('unknown_restaurant 31', RD), ('→ 112 rows to quarantine', G)], size=7.6),
    term([('1033 Rohan  Bengaluru    Basic', W), ('1033 Rohan  Navi Mumbai  Basic', Y), ('1033 Rohan  Navi Mumbai  Silver', Y), ('469 customers changed', G)], size=7.4),
    term([('Mumbai  12119  4277880', RD), ('(duplicates, refunds,', W), (' cancelled, lost NA rows)', W), ('→ build silver and gold', G)], size=7.6),
]
def flow(hi):
    o = ''
    for k, (name, sub, x, y) in enumerate([('landing files', '94 files', 14, 40), ('raw tables', 'all STRING', 130, 40), ('profile', 'counts, keys, rules', 246, 40),
                                           ('fact grain', 'one order', 14, 112), ('SCD 2 dim', 'customer history', 130, 112), ('gold', 'city × day', 246, 112)]):
        o += opbox(x, y, name, sub, 'acc' if k == hi else ['card', 'blue', 'violet', 'green', 'violet', 'green'][k], 100, 30)
    o += arrow(116, 55, 128, 55, 'ink3', 1.4) + arrow(232, 55, 244, 55, 'ink3', 1.4) + arrow(296, 72, 64, 110, 'ink3', 1.2, True)
    return o
B1 = [
    t(180, 22, 'Folders become partitions', 9.4, bold=True) + flow(1) + cap('Raw = exactly what arrived.', '', 'blue', y=172, h=34),
    t(180, 22, 'A log of versions, not a table', 9.4, bold=True) + flow(3) + cap('Grain: one order, newest version.', '', 'green', y=172, h=34),
    t(180, 22, 'Two dates per row', 9.4, bold=True) + flow(5) + cap('load_date for loads, order_date for reports.', '', 'amber', y=172, h=34),
    t(180, 22, 'Every rule gets a name', 9.4, bold=True) + flow(2) + cap('Quarantine with a reason, never drop.', '', 'amber', y=172, h=34),
    t(180, 22, 'History matters for analysis', 9.4, bold=True) + flow(4) + cap('Plan at the time of the order.', '', 'violet', y=172, h=34),
    t(180, 22, 'Design before code', 9.4, bold=True) + flow(5) + cap('Lesson 12.2 builds exactly this.', '', 'green', y=172, h=34),
]
see_caps = ['94 files, 31 loads, registered as partitions.',
            '546 copies and 660 second versions.',
            '2,078 rows describe an earlier day.',
            'Five rules, 112 broken rows.',
            'Customers move and change plans.',
            'The old report summed all of it.']
behind_caps = ['Raw tables keep every value as text.',
               'The fact needs a key and an upsert.',
               'Partition by event date; rebuild touched dates.',
               'Each rule becomes a reject reason.',
               'dim_customer keeps every version.',
               'The star schema answers the CEO correctly.']
two = anim_two('Profiling before building', 'From files to a design', 'Real lab outputs', 'What each finding decides', see, B1, see_caps, behind_caps)

# ---- scenario 1: requirement interview
e1 = (t(180, 22, '“Revenue per city”', 9.4, bold=True) + t(180, 56, 'Ask: gross or net? which date?', 8.4, 'ink2') + cap('Every KPI hides two questions.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Net = delivered only', 9.4, bold=True) + t(180, 56, 'refunds and cancellations out', 8.4, 'ink2') + cap('Write the definition down.', '', 'green', y=150, h=34))
e3 = (t(180, 22, 'By order date', 9.4, bold=True) + t(180, 56, 'not the date the file arrived', 8.4, 'ink2') + cap('Late rows change old days.', '', 'amber', y=150, h=34))
e4 = (t(180, 22, 'Freshness: by 06:00', 9.4, bold=True) + t(180, 56, 'nightly batch is enough', 8.4, 'ink2') + cap('No streaming needed.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Signed-off KPI sheet', 9.4, 'acc', bold=True) + t(180, 56, 'name · formula · grain · owner', 8.2, 'ink2') + cap('Now design starts.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Turning a vague question into a KPI',
              'What a data engineer asks before building anything. (Typical requirement meeting.)',
              'Requirement meeting', 'A vague question becomes a written KPI: gross or net, which date, how fresh, and who owns it', [e1, e2, e3, e4, e5],
              ['Revenue means what?',
               'Define net revenue.',
               'Choose the date.',
               'Agree on freshness.',
               'Get it signed off.'],
              hid='scenario-kpi')

# ---- scenario 2: profile surprises
b1 = (t(180, 22, 'New source: wallet top-ups', 9.4, bold=True) + t(180, 56, '“the key is txn_id”', 8.4, 'ink2') + cap('A claim to verify.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'COUNT vs COUNT(DISTINCT)', 9.4, bold=True) + t(180, 56, '2.1 M rows, 1.9 M ids', 8.4, 'ink', mono=True) + cap('Not unique.', '', 'amber', y=150, h=34))
b3 = (t(180, 22, 'Look at one id', 9.4, bold=True) + t(180, 56, 'PENDING → SUCCESS versions', 8.4, 'ink2') + cap('A status log.', '', 'amber', y=150, h=34))
b4 = (t(180, 22, 'Decide the grain', 9.4, bold=True) + t(180, 56, 'one row per txn, latest status', 8.4, 'ink2') + cap('Same pattern as orders.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Write it in the design doc', 9.4, 'acc', bold=True) + t(180, 56, 'key · version column · rule', 8.2, 'ink2') + cap('Before the first CREATE TABLE.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'The key that was not a key',
              'Step 4 on a different source. (Illustrative numbers.)',
              'Key check', 'Comparing COUNT and COUNT DISTINCT shows the key is not unique; the rows are status versions, so the grain is the latest version', [b1, b2, b3, b4, b5],
              ['Trust, but check.',
               'Counts disagree.',
               'Versions explain it.',
               'Grain decided.',
               'Documented.'],
              hid='scenario-key')

# ---- scenario 3: partition choice
u1 = (t(180, 22, 'How to partition the fact?', 9.4, bold=True) + t(180, 56, 'load_date or order_date?', 8.4, 'ink2') + cap('A classic design question.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'Reports filter by order_date', 9.4, bold=True) + t(180, 56, 'WHERE order_date BETWEEN …', 8.4, 'ink', mono=True) + cap('Pruning needs that column.', '', 'green', y=150, h=34))
u3 = (t(180, 22, 'Late rows touch old partitions', 9.4, bold=True) + t(180, 56, 'MERGE writes into old dates', 8.4, 'ink2') + cap('Acceptable with ACID.', '', 'amber', y=150, h=34))
u4 = (t(180, 22, 'Keep load_date as a column', 9.4, bold=True) + t(180, 56, 'for audit and re-runs', 8.4, 'ink2') + cap('Best of both.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Size check', 9.4, 'acc', bold=True) + t(180, 56, '~1,500 rows per day: small files', 8.2, 'ink2') + cap('Review this in Lesson 12.3.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Choosing the fact table’s partition column',
              'The trade-off behind one line of DDL.',
              'Partition choice', 'Partition by the date users filter on, keep the load date as a column, and check partition size', [u1, u2, u3, u4, u5],
              ['Two candidate columns.',
               'Follow the queries.',
               'Accept late writes.',
               'Keep both dates.',
               'Watch partition size.'],
              hid='scenario-partition')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>From landing files to a design</h2>
  <p>Left: the real profiling outputs. Right: the design decision each finding forces.</p>
''' + two + '''
  <p>Three live scenarios follow: a requirement meeting, a key that was not a key, and choosing a partition column.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Where this first phase happens at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'KPI sheet', 10, 'blue', bold=True) + t(60, 58, 'signed off', 7.4, 'ink2'),
    '1. Starting any analytics project',
    'Teams write a KPI definition sheet (name, formula, grain, owner, freshness) before building tables, so finance and product get the same number.',
    ['Business question', '*KPI definition', 'Design']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'profile', 11, 'green', bold=True) + t(60, 58, 'new source', 7.4, 'ink2'),
    '2. Onboarding a new source system',
    'Before a new payment or partner feed is connected, engineers profile a sample: key uniqueness, null rates, formats, volumes per day.',
    ['Sample files', '*profiling queries', 'Rules']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'SCD 2', 12, 'violet', bold=True) + t(60, 58, 'history', 7.4, 'ink2'),
    '3. Customer and product history',
    'Banks, insurers and retailers keep customer segment, branch or price history so old transactions are reported with the values valid at the time.',
    ['Change feed', '*SCD type 2', 'As-of reports']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'late', 12, 'acc', bold=True) + t(60, 58, 'data', 7.4, 'ink2'),
    '4. Late and corrected data',
    'Telecom usage records, delivery events and payment settlements often arrive days late; warehouses re-compute the affected days.',
    ['Late rows', '*touched dates', 'Rebuilt reports']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'audit', 11, 'acc', bold=True) + t(60, 58, 'trust', 7.4, 'ink2'),
    '5. Regulated reporting',
    'Regulators and auditors ask how many records arrived, how many were rejected and why. Quarantine and audit tables answer that.',
    ['Load', '*audit + quarantine', 'Evidence']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> this capstone uses external tables and loading (<a href="../../02-hiveql/02-managed-vs-external-tables/">2.2</a>, <a href="../../02-hiveql/05-loading-data/">2.5</a>), JSON (<a href="../../04-complex-data/03-json-and-semi-structured-data/">4.3</a>), partitions and MSCK (<a href="../../05-partitioning-and-bucketing/02-dynamic-partitions-and-msck/">5.2</a>) and ACID/MERGE (<a href="../../07-acid-and-iceberg/02-merge-and-scd/">7.2</a>). The lab is the Hive 4.2.1 Docker setup from <a href="../../01-introduction/05-install-hive-and-beeline/">Lesson 1.5</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
