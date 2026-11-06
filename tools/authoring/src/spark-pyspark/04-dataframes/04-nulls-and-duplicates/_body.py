import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
C = 'l44_nulls.txt'
def sec(a, b=None, drop=()):
    s = capsec(C, a, b, drop)
    s = re.sub(r'#\d+L?', '', s)
    return '\n'.join(l if len(l) <= 130 else l[:127] + ' …' for l in s.split('\n'))

def grid(x, y, rows, hi=(), cw=46, ch=16, dim=()):
    """small table: rows of cell strings; hi = set of (r,c) to highlight green, dim = rows to strike."""
    o = ''
    for r, row in enumerate(rows):
        for c, v in enumerate(row):
            tone = 'acc' if (r, c) in hi else ('green' if r in dim else 'card')
            o += box(x + c * cw, y + r * ch, cw - 2, ch - 2, tone, rx=2) + t(x + c * cw + cw / 2 - 1, y + r * ch + 10.5, v, 6.6, 'ink' if v != 'null' else 'red', mono=True)
    return o

ROWS = [['1425', 'Pune', '25', '4.5'], ['1738', 'null', '32', 'null'], ['2977', 'null', 'null', '3.5'], ['1425', 'Pune', '25', '4.5']]

# ---------------------------------------------------------------- story
sc_ = (grid(14, 30, ROWS, hi={(1, 1), (1, 3), (2, 1), (2, 2)}) + t(106, 104, '2,200 sign-ups · 2,000 users', 7.4, 'ink2') +
       box(400, 12, 232, 132, 'card') + t(516, 30, 'Measured', 8.6, bold=True) +
       ''.join(t(412, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ("= 'Pune' 404 + != 'Pune' 1642", 'amber'), ('…= 2046, not 2200 (154 null)', 'red'),
           ('avg(age) 38.9 vs sum/rows 36.8', 'amber'), ('na.drop() keeps 742 of 2200', 'red'),
           ('dropDuplicates: 3 runs, 3 answers', 'red'), ('row_number(): same every run', 'green')])))
scene_svg = scene('Real exports contain missing values and duplicate rows. We cleaned 2,200 sign-up rows from the TiffinGo app and measured how nulls change filters, averages and counts, and which duplicate Spark keeps.', sc_,
                  'Null is <tspan font-weight="700" class="s-acc">unknown</tspan>, not empty; a duplicate needs a <tspan font-weight="700" class="s-acc">rule</tspan> for which copy wins.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“The numbers don’t add up”</h2>
  <div class="story">
    <p class="narration">Marketing asked Kabir how many sign-ups came from outside Pune. He filtered <code>city != 'Pune'</code> and got 1,642. Pune had 404. The export had 2,200 rows. Where were the other 154? And when he removed duplicate users and re-ran the job, the “first sign-up date” changed every time.</p>

{scene_svg}

K> Sir, 404 plus 1,642 is not 2,200. Is Spark losing rows?
A> No. 154 rows have <b>no city</b>. For them, <code>city != 'Pune'</code> is neither true nor false, it is <b>null</b>, and a filter keeps only true. That is SQL’s three-valued logic.
R> And the changing dates?
A> <code>dropDuplicates</code> keeps <b>some</b> row per user, not a particular one. Today we find nulls, see how they behave in comparisons and aggregates, drop and fill them correctly, and remove duplicates in a way that gives the same answer every run. All outputs are real (PySpark 4.3.0).
  </div>
</section>
'''

lv = '''
LEVELS> Nulls and duplicates at three levels
L1> A class register
      <ul>
        <li>A blank in the register means “we don’t know”, not “absent” and not zero. You cannot say whether that student is from Pune or not.</li>
        <li>An average of marks counts only students with marks; blanks are left out.</li>
        <li>If a student is written twice, you must decide which line to keep: the first admission, the latest address?</li>
      </ul>
L2> The API
      <ul>
        <li>Find: <code>isNull()</code>, <code>isNotNull()</code>, <code>F.isnan()</code>, a null count per column. Compare safely: <code>eqNullSafe</code> (<code>&lt;=&gt;</code> in SQL).</li>
        <li>Fix: <code>df.na.drop(how, thresh, subset)</code>, <code>df.na.fill(value or dict)</code>, <code>df.na.replace()</code>, <code>F.coalesce()</code>; at read time <code>nullValue="NA"</code>.</li>
        <li>Duplicates: <code>distinct()</code>, <code>dropDuplicates(subset)</code>, or a window with <code>row_number()</code> to choose the copy.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li><code>= 'Pune'</code> (404) + <code>!= 'Pune'</code> (1,642) missed the 154 null cities; <code>avg(age)</code> 38.9 ignored 118 nulls.</li>
        <li><code>na.fill(0)</code> filled only numeric columns, <code>na.fill("unknown")</code> only strings; <code>na.drop()</code> kept just 742 of 2,200 rows.</li>
        <li><code>dropDuplicates(["user_id"])</code> kept 2,000 rows but different ones on each partitioning; <code>row_number()</code> gave the same rows every time.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Nulls and duplicates</h2>
''' + def_block(
    'In Spark SQL, <b>null</b> represents a missing or unknown value of any type. Comparisons and arithmetic with null yield null (three-valued logic), filters keep only rows whose predicate is true, and aggregate functions such as <code>count(col)</code>, <code>sum</code> and <code>avg</code> ignore nulls, while <code>count(*)</code> counts rows. <b>NaN</b> is a distinct floating-point value (“not a number”), not null. <code>DataFrameNaFunctions</code> (<code>df.na</code>) provide <code>drop</code>, <code>fill</code> and <code>replace</code>; <code>fill</code> applies a value only to columns of a compatible type. <b>Duplicates</b> are removed with <code>distinct()</code> (all columns) or <code>dropDuplicates(subset)</code>, which keeps an arbitrary row per key and is therefore non-deterministic unless the choice is made explicit, typically with <code>row_number()</code> over a window ordered by a tiebreaker.',
    'A null means “we don’t know this value”. Spark skips nulls in sums and averages and treats “unknown = something” as unknown, so filters can quietly leave rows out. Find nulls first, then drop or fill them on purpose. To remove duplicates, decide which copy you want and tell Spark, otherwise it may pick a different one each run.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('null', 'Missing or unknown value.'),
    ('NaN', 'Floating “not a number”; not the same as null.'),
    ('Three-valued logic', 'true, false and null (unknown).'),
    ('eqNullSafe / &lt;=&gt;', 'Equality where null equals null.'),
    ('df.na', 'drop, fill and replace helpers.'),
    ('coalesce()', 'First non-null value from several columns.'),
    ('dropDuplicates', 'Keep one row per key (which one is not fixed).'),
    ('row_number()', 'Number rows per key in a chosen order.'),
]) + '''

  <h3>How nulls behave</h3>
''' + table(['Expression', 'Result', 'Lab'], [
    ['<code>NULL = NULL</code>', 'NULL', 'eq: NULL'],
    ['<code>NULL &lt;=&gt; NULL</code>', 'true', 'null_safe: true'],
    ['<code>NULL &gt; 1</code>, <code>NOT NULL</code>', 'NULL', 'NULL'],
    ['<code>NULL AND false</code> / <code>NULL OR true</code>', 'false / true', 'false / true'],
    ['<code>WHERE city != \'Pune\'</code>', 'null rows dropped', '1,642 (154 missing)'],
    ['<code>count(age)</code> vs <code>count(*)</code>', 'nulls skipped vs counted', '2,082 vs 2,200'],
    ['<code>avg(age)</code>', 'average of known values', '38.85 (not 36.77)'],
], minw=640) + lv + '''
EXAM> “Why can count(*) and count(col) differ?” <code>count(*)</code> counts rows; <code>count(col)</code> counts non-null values of that column. In our sign-ups 2,200 rows had 2,082 known ages. The same rule makes <code>avg</code> the average of known values only.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Which kind of “missing”?</h2>
''' + table(['In the raw data', 'What Spark reads', 'How to handle'], [
    ['Empty CSV field', 'null (numbers and strings)', 'Already null'],
    ['<code>NA</code>, <code>N/A</code>, <code>-</code>', 'The string itself', '<code>nullValue="NA"</code> or <code>na.replace</code>'],
    ['<code>NaN</code> in a number column', 'NaN (a double), not null', '<code>F.isnan()</code>; convert to null with <code>when</code>'],
    ['<code>""</code> in JSON', 'Empty string, not null', '<code>F.when(F.col(c) == "", None)</code>'],
    ['A bad value (<code>abc</code>)', 'Error or null after <code>try_cast</code>', 'Lesson 4.3'],
    ['A missing JSON key', 'null', 'Already null'],
], minw=640) + '''
WARN> Do not fill nulls just to make them disappear. Filling age with 0 drags the average down; filling city with “unknown” is fine for a report but wrong for a delivery address. Decide per column: drop the row, fill with a meaningful default, or keep the null and handle it downstream.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Cleaning the sign-up export</h2>
  <p>All outputs are real: PySpark 4.3.0, local mode, a sign-up export of 2,200 rows (2,000 users) with blanks, <code>NA</code> strings, <code>NaN</code> ratings, 120 exact duplicates from app retries and 80 repeat sign-ups.</p>
''' + stepper([
    ('Step 1 · Count nulls per column',
     code('python', 'l44_nulls.py', 'raw = spark.read.csv(path, header=True, inferSchema=True)\ndef nulls(df):\n    return df.select([F.sum(F.col(c).isNull().cast("int")).alias(c) for c in df.columns])\nnulls(raw).show()\nraw.where("city = \'NA\'").count(), raw.where(F.isnan("rating")).count()', sec('== 1)', '== 2)')),
     'Empty fields became null, but <b>61 cities were the text <code>NA</code></b> and 366 ratings were <b>NaN</b>, neither of which counts as null. Note also that <code>phone</code> was inferred as <code>long</code>: phone numbers should be strings (Lesson 4.2). One <code>select</code> with a null count per column is the first thing to run on any new dataset.'),
    ('Step 2 · Make all “missing” values null',
     code('python', 'l44_nulls.py', 's = spark.read.csv(path, header=True, inferSchema=True, nullValue="NA")\nnulls(s).show()\ns = s.withColumn("rating", F.when(F.isnan("rating"), None).otherwise(F.col("rating")))', sec('== 2)', '== 3)')),
     '<code>nullValue="NA"</code> turned the 61 <code>NA</code> cities into nulls (93 + 61 = 154). NaN is a valid double, so it needed its own step: after the <code>when</code>, rating has 410 + 366 = 776 nulls. Now one rule handles all missing values.'),
    ('Step 3 · Comparisons with null',
     code('python', 'l44_nulls.py', 'spark.sql("SELECT NULL = NULL AS eq, NULL <=> NULL AS null_safe, NULL > 1 AS gt, NOT NULL AS not_null, NULL AND false AS and_false, NULL OR true AS or_true").show()\ns.where(F.col("city") == "Pune").count(); s.where(F.col("city") != "Pune").count()\ns.where(F.col("city").isNull()).count()\ns.where(~F.col("city").eqNullSafe("Pune")).count()', sec('== 3)', '== 4)')),
     'Here is Kabir’s puzzle: 404 + 1,642 = 2,046, and the 154 null cities are in neither, because <code>null != \'Pune\'</code> is null and filters keep only true. Use <code>isNull()</code> to find them, or <code>eqNullSafe</code>, which treats null as a normal value: “not Pune” then gives 1,796 = 1,642 + 154.'),
    ('Step 4 · Aggregates skip nulls',
     code('python', 'l44_nulls.py', 's.select(F.count("*").alias("rows"), F.count("age").alias("count_age"), F.avg("age").alias("avg_age"),\n         F.sum("age").alias("sum_age"), (F.sum("age") / F.count("*")).alias("sum_over_rows")).show()', sec('== 4)', '== 5)')),
     '<code>count("age")</code> counted 2,082 known ages, not 2,200 rows; <code>avg</code> divided by 2,082, giving 38.85. Dividing the sum by all rows gives 36.77, as if missing ages were 0. Both are “correct”; know which question you are answering.'),
    ('Step 5 · Drop and fill',
     code('python', 'l44_nulls.py', 's.na.drop().count(); s.na.drop(how="all").count()\ns.na.drop(thresh=6).count(); s.na.drop(subset=["city", "phone"]).count()\ns.na.fill(0); s.na.fill("unknown")\ns.na.fill({"city": "unknown", "referral": "none", "age": -1})\nF.coalesce(F.col("phone").cast("string"), F.lit("no phone"))\ns.na.replace({"INSTA": "Instagram"}, subset=["referral"])', sec('== 5)', '== 7)')),
     '<code>na.drop()</code> with the default <code>how="any"</code> threw away <b>two thirds</b> of the data (742 left), because almost every row misses something. <code>thresh</code> and <code>subset</code> are what you usually want. <code>na.fill</code> is <b>type-aware</b>: <code>fill(0)</code> touched only numeric columns, <code>fill("unknown")</code> only strings. A dict sets a value per column.'),
    ('Step 6 · Duplicates, and which row survives',
     code('python', 'l44_nulls.py', 's.distinct().count(); s.dropDuplicates(["user_id"]).count()\nfor parts in (1, 3, 7):\n    k = s.repartition(parts).dropDuplicates(["user_id"])\n    k.agg(F.sum(F.unix_timestamp("signed_up_at")))      # checksum of kept rows\nw = Window.partitionBy("user_id").orderBy(F.col("signed_up_at").asc(), F.col("city").asc_nulls_last())\ns.withColumn("rn", F.row_number().over(w)).where("rn = 1")\ns.dropDuplicates(["user_id"]).explain()', sec('== 7)')),
     '<code>distinct()</code> removed the 120 exact copies (2,080 left); <code>dropDuplicates(["user_id"])</code> also removed the 80 repeat sign-ups (2,000). But the checksum of the kept rows <b>changed with the partitioning</b>: the plan shows why, it is a group-by on <code>user_id</code> with <code>first()</code> of every other column, and “first” depends on row order. <code>row_number()</code> over a window ordered by sign-up time (plus a tiebreaker) gave the same rows every run.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('nulls: city 93, rating 410', W), ("city = 'NA'  : 61   (not null!)", Y), ('rating NaN   : 366  (not null!)', Y)], size=7.4),
    term([("= 'Pune' 404, != 'Pune' 1642", W), ('missing: 154 null cities', RD), ('NOT eqNullSafe Pune: 1796', G)], size=7.4),
    term([('count(*)   2200, count(age) 2082', W), ('avg(age)   38.85', G), ('sum/rows   36.77', Y)], size=7.4),
    term([('na.drop()        : 742 left', RD), ('na.drop(thresh=6): 2152', G), ('fill(0): numbers only', Y)], size=7.4),
    term([('dropDuplicates checksums:', W), ('…503320, …739660, …764920', RD), ('row_number: same 3 times', G)], size=7.4),
]
B1 = [
    t(180, 14, 'Three kinds of missing', 9.4, bold=True) + grid(40, 32, [['""', 'NA', 'NaN'], ['null', 'text', 'double']], cw=92, ch=22) + cap('Only one of them is null.', '', 'amber', y=144, h=30),
    t(180, 14, 'Unknown is not false', 9.4, bold=True) + flow([("city != 'Pune'", 'null city', 'card'), ('NULL', 'unknown', 'acc'), ('filter', 'drops it', 'red')], y=48, w=96, gap=22) + cap('Filters keep only true.', '', 'red', y=144, h=30),
    t(180, 14, 'Aggregates skip nulls', 9.4, bold=True) + grid(60, 34, [['25'], ['32'], ['null'], ['41']], cw=60, ch=18) + t(220, 52, 'avg = 98 / 3', 8.2, 'green', anchor='start', mono=True) + t(220, 72, 'not 98 / 4', 8.2, 'red', anchor='start', mono=True) + cap('count(col) counts known values.', '', 'blue', y=144, h=30),
    t(180, 14, 'Drop or fill on purpose', 9.4, bold=True) + grid(40, 32, ROWS[:3], hi={(1, 1), (1, 3), (2, 1), (2, 2)}) + flow([('drop any', '742 left', 'red'), ('thresh / subset', 'keep most', 'green')], x0=60, y=92, w=110, gap=30) + cap('fill() matches value types.', '', 'violet', y=144, h=30),
    t(180, 14, 'Which duplicate survives?', 9.4, bold=True) + grid(40, 32, [['1425', '10-15 03:55'], ['1425', '10-17 11:02']], cw=70, ch=20) + flow([('first()', 'any row', 'red'), ('row_number', 'ordered', 'green')], x0=200, y=34, w=70, gap=10) + cap('Make the choice explicit.', '', 'green', y=144, h=30),
]
see_caps = ['Two kinds of missing were not null.', '154 rows fell out of both filters.', 'avg ignored 118 missing ages.', 'drop() removed two thirds.', 'dropDuplicates changed; row_number did not.']
behind_caps = ['Normalise all missing values to null.', 'Three-valued logic.', 'Nulls are skipped by aggregates.', 'Use thresh and subset.', 'first() depends on row order.']
two = anim_two('Nulls and duplicates', 'Unknown values, repeated rows', 'Real lab outputs', 'What Spark does', see, B1, see_caps, behind_caps)

# ---- scenario 1: campaign count
e1 = (t(180, 22, '“Sign-ups outside Pune?”', 9.4, bold=True) + t(180, 56, "where city != 'Pune' -> 1,642", 8.4, 'ink', mono=True) + cap('Sent to marketing.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Finance counts 2,200 rows', 9.4, bold=True) + t(180, 56, '404 + 1,642 = 2,046', 8.4, 'ink2') + cap('154 missing.', '', 'amber', y=150, h=34))
e3 = (t(180, 22, 'Null cities', 9.4, bold=True) + t(180, 56, "null != 'Pune' is null", 8.4, 'ink', mono=True) + cap('Filtered out silently.', '', 'red', y=150, h=34))
e4 = (t(180, 22, 'Report three buckets', 9.4, bold=True) + t(180, 56, 'Pune 404 · other 1,642 · unknown 154', 8.2, 'ink2') + cap('Totals reconcile.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Fix the form', 9.4, 'acc', bold=True) + t(180, 56, 'city required at sign-up', 8.4, 'ink2') + cap('Fewer nulls upstream.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'A report that lost 154 users',
              'Nulls in filters. (Numbers from our lab.)',
              'Null in filters', 'A not-equal filter drops null rows; report an unknown bucket so totals reconcile', [e1, e2, e3, e4, e5],
              ['Filter.', 'Totals differ.', 'Null rows.', 'Unknown bucket.', 'Fix upstream.'],
              hid='scenario-filter')

# ---- scenario 2: nondeterministic dedup
b1 = (t(180, 22, 'customers = dropDuplicates(id)', 9.4, bold=True) + t(180, 56, 'daily job', 8.4, 'ink2') + cap('First sign-up date per user.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'Re-run gives other dates', 9.4, bold=True) + t(180, 56, 'auditors ask why numbers moved', 8.4, 'ink2') + cap('Nothing changed in the data.', '', 'amber', y=150, h=34))
b3 = (t(180, 22, 'first() of each column', 9.4, bold=True) + t(180, 56, 'depends on partitions and order', 8.4, 'ink2') + cap('Like our three checksums.', '', 'red', y=150, h=34))
b4 = (t(180, 22, 'row_number over a window', 9.4, bold=True) + t(180, 56, 'order by signed_up_at, tiebreaker', 8.2, 'ink', mono=True) + cap('Same rows every run.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Or max_by / min_by', 9.4, 'acc', bold=True) + t(180, 56, 'groupBy(id).agg(min_by(city, ts))', 8.2, 'ink', mono=True) + cap('Lesson 6.1.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Deduplication that changes every run',
              'Deterministic deduplication. (Behaviour from our lab.)',
              'Non-deterministic dropDuplicates', 'dropDuplicates keeps an arbitrary row per key; choose the row with row_number over an ordered window', [b1, b2, b3, b4, b5],
              ['Dedup.', 'Numbers move.', 'Arbitrary row.', 'row_number.', 'min_by.'],
              hid='scenario-dedup')

# ---- scenario 3: fill(0) bias
u1 = (t(180, 22, 'Model needs no nulls', 9.4, bold=True) + t(180, 56, 'df.na.fill(0)', 8.4, 'ink', mono=True) + cap('Quick fix.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'Average customer age: 36.8', 9.4, bold=True) + t(180, 56, 'real known average: 38.9', 8.4, 'ink2') + cap('Zeros pulled it down.', '', 'amber', y=150, h=34))
u3 = (t(180, 22, 'Ratings of 0 stars', 9.4, bold=True) + t(180, 56, 'NaN and blanks became 0.0', 8.4, 'ink2') + cap('Fake bad reviews.', '', 'red', y=150, h=34))
u4 = (t(180, 22, 'Fill per column', 9.4, bold=True) + t(180, 56, 'median age + is_age_missing flag', 8.4, 'ink2') + cap('Keep the information.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Imputer in MLlib', 9.4, 'acc', bold=True) + t(180, 56, 'mean / median strategies', 8.4, 'ink2') + cap('Module 10.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'fill(0) that biased a model',
              'Filling nulls responsibly. (Numbers from our lab.)',
              'Fill bias', 'Filling numeric nulls with zero changes averages and distributions; fill per column and keep a missing flag', [u1, u2, u3, u4, u5],
              ['fill(0).', 'Average drops.', 'Fake zeros.', 'Per-column fill.', 'Imputer.'],
              hid='scenario-fill')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Unknown values, repeated rows</h2>
  <p>Left: real outputs. Right: what Spark does with them.</p>
''' + two + '''
  <p>Three live scenarios follow: a report that lost users, deduplication that changes every run, and a fill that biased a model.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Data cleaning at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'profile', 11, 'blue', bold=True) + t(60, 58, 'null counts', 7.4, 'ink2'),
    '1. Data profiling',
    'Ingestion jobs record null counts per column every day and alert when a column suddenly has many more.',
    ['New file', '*null counts', 'Alert']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'CDC', 12, 'green', bold=True) + t(60, 58, 'latest row', 7.4, 'ink2'),
    '2. Latest version of a record',
    'Change feeds keep the newest row per key with row_number ordered by update time.',
    ['Changes', '*row_number', 'Current table']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'retries', 11, 'violet', bold=True) + t(60, 58, 'events', 7.4, 'ink2'),
    '3. Retried events',
    'Apps resend events on bad networks; exact copies are removed by event id before counting.',
    ['Events', '*dropDuplicates(id)', 'True counts']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'reports', 11, 'acc', bold=True) + t(60, 58, 'unknown', 7.4, 'ink2'),
    '4. Honest reports',
    'Dashboards show an “unknown” category so totals match and data gaps stay visible.',
    ['Null city', '*coalesce("unknown")', 'Report']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'ML', 12, 'acc', bold=True) + t(60, 58, 'imputation', 7.4, 'ink2'),
    '5. Model features',
    'Missing values are filled per feature with medians and an is_missing flag, not with zeros.',
    ['Features', '*fill + flag', 'Training']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> columns, <code>when</code> and filters in <a href="../03-working-with-columns/">4.3</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
