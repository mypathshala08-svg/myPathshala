import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
C = 'l73_catalyst.txt'
def sec(a, b=None, drop=()):
    s = capsec(C, a, b, drop)
    s = re.sub(r'#\d+L?', '', s)
    return '\n'.join(l if len(l) <= 130 else l[:127] + ' …' for l in s.split('\n'))
def part(name, nxt):
    s = sec(name, nxt)
    return s
PARSED = part('== Parsed Logical Plan ==', '== Analyzed')
OPT = part('== Optimized Logical Plan ==', '== Physical Plan ==')
PHYS = part('== Physical Plan ==', '== 2)')
FMT = sec('(1) Scan parquet', '(2) Filter')
S6 = re.sub(r'\n(bad|good): [\d.]+ s', '', sec('== 6)', '== 7)'))

PHASES = [('Parsed', 'unresolved', 'card'), ('Analyzed', 'names, types', 'blue'), ('Optimized', 'rules', 'violet'), ('Physical', 'strategies', 'green')]

# ---------------------------------------------------------------- story
sc_ = (flow(PHASES, y=36, x0=6, w=76, gap=12) + t(184, 96, 'filters moved below the join', 7.2, 'green') + t(184, 110, '((1 + 1) + 798) → 800', 7.2, 'green', mono=True) + t(184, 124, 'only 4 of 6 columns read', 7.2, 'green') +
       box(400, 12, 232, 132, 'card') + t(516, 30, 'Measured', 8.6, bold=True) +
       ''.join(t(412, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ('4 plans from explain(extended)', 'ink'), ('filters pushed below join', 'green'),
           ('5 filters pushed into Parquet', 'green'), ('broadcast chosen for customers', 'green'),
           ('"bad" and "good" code: same plan', 'green'), ('UDF filter: nothing pushed', 'red')])))
scene_svg = scene('Catalyst is the optimizer behind DataFrames and Spark SQL. It turns your query into four plans: parsed, analyzed, optimized and physical. We read each plan for a join query and proved that two differently written queries become the same plan.', sc_,
                  'Write <tspan font-weight="700" class="s-acc">clear</tspan> code; read <tspan font-weight="700" class="s-acc">explain()</tspan> to see what Spark will really do.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Should I filter before or after the join?”</h2>
  <div class="story">
    <p class="narration">During code review Riya rewrote a colleague’s query to filter orders <b>before</b> the join instead of after it, select columns early and precompute constants, “for performance”. Arjun Sir asked her to compare the two plans first.</p>

{scene_svg}

R> Sir, filtering first must be faster. Fewer rows to join.
A> Of course, and Catalyst already does it for you: it pushes filters down, prunes columns and folds constants before running anything. Both versions produced exactly the <b>same optimized plan</b>.
K> Then how do we know what Spark will really do?
A> With <code>explain()</code>. Today we read all four plans of a join query, the formatted and cost views, whole-stage code generation, prove that two styles give the same plan, and see the one thing Catalyst cannot optimise. All outputs are real (PySpark 4.3.0).
  </div>
</section>
'''

lv = '''
LEVELS> Catalyst at three levels
L1> A route planner
      <ul>
        <li>You tell the map app where to go; it reads the request (parse), checks the places exist (analyze), finds shortcuts (optimize) and picks roads and vehicles (physical plan).</li>
        <li>Two people describing the same trip in different words get the same route.</li>
        <li>A stop the app knows nothing about (a UDF) cannot be optimised around.</li>
      </ul>
L2> The API
      <ul>
        <li><code>df.explain()</code> (physical), <code>explain(mode="extended")</code> (all four), <code>"formatted"</code> (numbered operators with details), <code>"cost"</code> (statistics), <code>"codegen"</code> (generated Java).</li>
        <li>In SQL: <code>EXPLAIN [EXTENDED | FORMATTED | COST | CODEGEN] SELECT …</code>.</li>
        <li>Look for: <code>PushedFilters</code>, <code>ReadSchema</code>, join strategy, <code>Exchange</code> (shuffles), <code>*(n)</code> code-generated stages.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>Two filters written after a join were moved below it and into both scans; <code>(1 + 1) + 798</code> became <code>800</code>.</li>
        <li>Parquet received 5 pushed filters and read 4 of 6 columns; the 2,000-row customer table was broadcast.</li>
        <li>A “bad” and a “good” version of a query had identical optimized plans; a UDF filter pushed nothing.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>The Catalyst optimizer</h2>
''' + def_block(
    '<b>Catalyst</b> is Spark SQL’s extensible query optimizer. A query from SQL or the DataFrame API passes through four phases: an <b>unresolved (parsed) logical plan</b>; <b>analysis</b>, which resolves names and types against the catalog; <b>logical optimization</b>, which applies rule-based rewrites such as predicate pushdown, column pruning, constant folding and filter combination (and cost-based join reordering when statistics are available); and <b>physical planning</b>, which chooses operators such as broadcast hash or sort-merge joins. The physical plan is then compiled by <b>whole-stage code generation</b> (Tungsten) into Java bytecode that fuses operators. With Adaptive Query Execution the physical plan can be revised at run time (Lesson 7.4). <code>explain()</code> displays these plans.',
    'Catalyst rewrites your query into the fastest plan it can find: it moves filters to the data, reads only needed columns, simplifies expressions and picks join methods. explain() shows you the result, so you can check what Spark will really do.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Logical plan', 'What to compute.'),
    ('Physical plan', 'How to compute it (operators, joins, shuffles).'),
    ('Analyzer', 'Resolves column and table names.'),
    ('Predicate pushdown', 'Filters moved toward or into the data source.'),
    ('Column pruning', 'Only needed columns are read.'),
    ('Constant folding', 'Expressions of constants computed once.'),
    ('Whole-stage codegen', 'Operators fused into generated Java: *(n).'),
    ('Exchange', 'A shuffle in the physical plan.'),
]) + '''

  <h3>explain modes</h3>
''' + table(['Mode', 'Shows', 'Use it to'], [
    ['<code>simple</code> (default)', 'Physical plan', 'see joins, shuffles, scans'],
    ['<code>extended</code>', 'Parsed, analyzed, optimized, physical', 'see what the optimizer changed'],
    ['<code>formatted</code>', 'Operator list + details per operator', 'read PushedFilters, ReadSchema, join keys'],
    ['<code>cost</code>', 'Optimized plan with statistics', 'check size estimates (broadcast decisions)'],
    ['<code>codegen</code>', 'Generated Java code', 'debug code generation'],
], minw=600) + lv + '''
EXAM> “What does Catalyst do?” It turns DataFrame/SQL queries into an optimized physical plan in four phases: parse, analyze (resolve names via the catalog), optimize logically with rules (predicate pushdown, column pruning, constant folding, CBO join reordering with stats) and plan physically (choose join and aggregation strategies), then whole-stage code generation compiles it. Write clear code; check with explain().
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Reading a physical plan</h2>
''' + table(['You see', 'It means', 'Watch for'], [
    ['<code>FileScan … PushedFilters: […]</code>', 'Filters sent to the file reader', 'Empty brackets on a filtered query'],
    ['<code>ReadSchema: struct&lt;…&gt;</code>', 'Columns actually read', 'All columns when you need two'],
    ['<code>Exchange hashpartitioning</code>', 'A shuffle', 'More shuffles than expected'],
    ['<code>BroadcastHashJoin</code> / <code>SortMergeJoin</code>', 'Join strategy', 'SMJ with a small side'],
    ['<code>*(n)</code>', 'Whole-stage codegen stage n', 'Operators outside codegen'],
    ['<code>BatchEvalPython</code> / <code>ArrowEvalPython</code>', 'Python UDF', 'Lost pushdown'],
    ['<code>AdaptiveSparkPlan isFinalPlan=false</code>', 'AQE will refine at run time', 'Read the final plan after running (7.4)'],
], minw=680) + '''
WARN> With AQE on (the default), <code>explain()</code> before execution shows the <b>initial</b> plan and hides code-generation markers. To see what really ran, look at the SQL tab of the Spark UI or call <code>explain()</code> on the DataFrame after an action, where the plan shows <code>isFinalPlan=true</code>.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Four plans for one join</h2>
  <p>All outputs are real: PySpark 4.3.0, local mode. The query joins 5,000,000 orders (Parquet) with 2,000 customers (CSV), adds GST, keeps Gold customers’ delivered orders above ₹800. Plan ids (<code>#12</code>) are removed for readability.</p>
''' + code('python', 'l73_catalyst.py', 'q = (o.join(c, "customer_id")\n      .withColumn("gst", F.col("amount") * F.lit(5) / F.lit(100))\n      .where((F.col("plan") == "Gold") & (F.col("status") == "DELIVERED"))\n      .where(F.col("amount") > F.lit(1) + F.lit(1) + F.lit(798))\n      .select("order_id", "name", "amount", "gst"))\nq.explain(mode="extended")') + stepper([
    ('Step 1 · Parsed and analyzed: what you wrote',
     code('text', 'parsed logical plan', '', PARSED) if False else code('text', 'explain(extended)', 'q.explain(mode="extended")   # first part', PARSED),
     'The parsed plan is your code, step by step, upside down: join first, then the new column, two separate filters, the projection. <code>((1 + 1) + 798)</code> is still an expression. The analyzed plan (same shape) adds resolved types and checks that every column exists, which is where typos fail (Lesson 4.3).'),
    ('Step 2 · Optimized: Catalyst’s rewrites',
     code('text', 'explain(extended)', 'q.explain(mode="extended")   # optimized part', OPT),
     'Everything moved. Both <code>where</code>s were combined and split by table: <code>status</code> and <code>amount</code> filters now sit <b>below the join</b> on orders, <code>plan = Gold</code> on customers, with added <code>isnotnull</code> checks for the join keys. <code>(1 + 1) + 798</code> was folded to <b>800</b>, <code>cast(100 as double)</code> to <code>100.0</code>. Each side keeps only the columns needed later.'),
    ('Step 3 · Physical: strategies and scans',
     code('text', 'explain(extended)', 'q.explain(mode="extended")   # physical part', PHYS),
     'The 2,000-row customer side was small enough to <b>broadcast</b>, so there is no shuffle of orders at all. Filters went even further: into the <code>FileScan</code> as <code>DataFilters</code>, and Parquet reads only <code>order_id, customer_id, amount, status</code>.'),
    ('Step 4 · explain("formatted") and explain("cost")',
     code('text', 'explain(formatted) / explain(cost)', 'q.explain(mode="formatted")\no.where("city = \'Pune\'").select("amount").explain(mode="cost")', FMT + '\n…\n' + sec('== 3)', '== 4)') if '== 4)' in open(os.path.join(HERE, '..', '..', 'lab', 'captures', C)).read() else FMT + '\n…\n' + sec('== 3)', '== 5)')),
     'The formatted view numbers each operator and lists its details: here the five <b>PushedFilters</b> handed to Parquet and the exact <code>ReadSchema</code>. The cost view shows size estimates: 34.6 MiB of Parquet, 6.1 MiB after projection. These estimates drive broadcast decisions; table statistics (Lesson 7.2) make them better.'),
    ('Step 5 · Whole-stage code generation',
     code('python', 'l73_catalyst.py', 'spark.conf.set("spark.sql.adaptive.enabled", "false")   # show the static plan\ns = o.where("amount > 800").agg(F.sum("amount"))\ns.explain(); s.explain(mode="codegen")', sec('== 5)', '== 6)')),
     'With AQE on, the plan printed before running did not show codegen; with the static plan, <code>*(1)</code> and <code>*(2)</code> mark two <b>code-generated stages</b> on either side of the shuffle. Scan, filter and partial sum were fused into one generated Java function (<code>processNext</code>, 267 lines of generated code), which is why built-in operations are so much faster than Python.'),
    ('Step 6 · Two styles, one plan; and a black box',
     code('python', 'l73_catalyst.py', 'bad = (o.withColumn("x", F.col("amount") * 2).join(c, "customer_id")\n        .where(F.col("city") == "Pune").select("order_id", "name"))\ngood = (o.where(F.col("city") == "Pune").select("order_id", "customer_id")\n         .join(c.select("customer_id", "name"), "customer_id").select("order_id", "name"))\n# compare optimized plans (ids removed)\no.where(udf(lambda a: a > 800, "boolean")("amount")).select("order_id").explain()', S6 + '\n' + sec('== 7)')),
     'The “bad” version computed an unused column, joined everything, then filtered; the “good” one filtered and projected first. Their optimized plans were <b>identical</b>: Catalyst removed the unused column and pushed the filter itself. Write the clearest code. The exception is a <b>UDF</b>: its filter stays above an <code>ArrowEvalPython</code> step with <code>DataFilters: []</code>, nothing pushed (Lesson 6.6).'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('Parsed: Filter (amount > ((1 + 1) + 798))', W), ('Filter (plan = Gold AND status = …)', W), ('Join Inner', W)], size=7.0),
    term([('Optimized: Join', W), ('  orders : Filter status, amount > 800', G), ('  custs  : Filter plan = Gold', G)], size=7.0),
    term([('BroadcastHashJoin BuildRight', G), ('FileScan parquet [order_id, …, status]', W)], size=7.2),
    term([('PushedFilters: [… EqualTo(status,…),', G), ('  GreaterThan(amount,800) …]', G), ('sizeInBytes=6.1 MiB', W)], size=7.2),
    term([('bad vs good: optimized plans identical', G), ('UDF: DataFilters: []', RD)], size=7.4),
]
B1 = [
    t(180, 14, 'Four phases', 9.4, bold=True) + flow(PHASES, y=50, x0=6, w=76, gap=12) + cap('Your code is the starting point.', '', 'blue', y=144, h=30),
    t(180, 14, 'Filters move down', 9.4, bold=True) + opbox(130, 30, 'Join', '', 'blue', 100, 24) + opbox(30, 76, 'orders', 'status, amount>800', 'green', 130, 30) + opbox(200, 76, 'customers', 'plan = Gold', 'green', 130, 30) + arrow(95, 76, 150, 54, 'ink3', 1.0) + arrow(265, 76, 210, 54, 'ink3', 1.0) + cap('Constants folded: 1+1+798 → 800.', '', 'violet', y=144, h=30),
    t(180, 14, 'Small side broadcast', 9.4, bold=True) + flow([('Parquet', '4 of 6 cols', 'green'), ('BHJ', 'no shuffle', 'blue'), ('result', '', 'card')], y=50, w=96, gap=22) + cap('Physical strategy from size estimates.', '', 'green', y=144, h=30),
    t(180, 14, 'Filters inside the reader', 9.4, bold=True) + opbox(30, 40, 'Parquet reader', '5 PushedFilters', 'green', 300, 34) + opbox(30, 86, 'ReadSchema', 'order_id, customer_id, amount, status', 'blue', 300, 30) + cap('formatted shows every detail.', '', 'blue', y=144, h=30),
    t(180, 14, 'Same plan, any style', 9.4, bold=True) + opbox(20, 40, 'bad code', '', 'acc', 100, 26) + opbox(20, 86, 'good code', '', 'green', 100, 26) + arrow(120, 53, 200, 70, 'ink3', 1.0) + arrow(120, 99, 200, 80, 'ink3', 1.0) + opbox(204, 60, 'one optimized plan', '', 'violet', 130, 30) + cap('Except UDFs: a black box.', '', 'amber', y=144, h=30),
]
see_caps = ['The plan as written.', 'Catalyst rewrote it.', 'A broadcast join and a narrow scan.', 'Pushed filters and estimates.', 'Equal plans; UDF blocks pushdown.']
behind_caps = ['Parse → analyze → optimize → plan.', 'Pushdown, pruning, folding.', 'Strategies chosen by size.', 'Data source receives filters.', 'Optimizer works on expressions.']
two = anim_two('Catalyst and explain', 'What Spark really runs', 'Real lab outputs', 'The plans', see, B1, see_caps, behind_caps)

e1 = (t(180, 22, 'Code review: “filter first!”', 9.4, bold=True) + t(180, 56, 'hours spent reordering code', 8.4, 'ink2') + cap('For performance.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Compare optimized plans', 9.4, bold=True) + t(180, 56, 'explain(mode="extended")', 8.4, 'ink', mono=True) + cap('Identical in our lab.', '', 'green', y=150, h=34))
e3 = (t(180, 22, 'Catalyst already pushed down', 9.4, bold=True) + t(180, 56, 'filters and column pruning', 8.4, 'ink2') + cap('Write the clearest code.', '', 'green', y=150, h=34))
e4 = (t(180, 22, 'Look for real problems', 9.4, bold=True) + t(180, 56, 'UDFs, extra shuffles, SMJ on small side', 8.2, 'ink2') + cap('Those change plans.', '', 'amber', y=150, h=34))
e5 = (t(180, 22, 'Review plans, not style', 9.4, 'acc', bold=True) + t(180, 56, 'attach explain output to PRs', 8.4, 'ink2') + cap('Evidence over intuition.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Reordering code that Catalyst reorders anyway',
              'Trusting and checking the optimizer. (Behaviour from our lab.)',
              'Optimizer rewrites', 'Catalyst pushes filters and prunes columns itself; compare plans before rewriting for performance', [e1, e2, e3, e4, e5],
              ['Review.', 'Compare.', 'Already done.', 'Real issues.', 'Plan reviews.'],
              hid='scenario-rewrite')
b1 = (t(180, 22, 'A slow nightly join', 9.4, bold=True) + t(180, 56, 'explain() shows SortMergeJoin', 8.4, 'ink', mono=True) + cap('Dimension is small.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'explain(mode="cost")', 9.4, bold=True) + t(180, 56, 'dim estimated at 2 GB', 8.4, 'ink2') + cap('Wrong estimate.', '', 'amber', y=150, h=34))
b3 = (t(180, 22, 'No statistics', 9.4, bold=True) + t(180, 56, 'estimate from file sizes only', 8.4, 'ink2') + cap('After a filter it is tiny.', '', 'amber', y=150, h=34))
b4 = (t(180, 22, 'ANALYZE TABLE / hint', 9.4, bold=True) + t(180, 56, 'or AQE switches at run time', 8.4, 'ink2') + cap('Lessons 7.2 and 7.4.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'BroadcastHashJoin', 9.4, 'acc', bold=True) + t(180, 56, 'no shuffle of the big table', 8.4, 'ink2') + cap('Job much faster.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'The plan chose the wrong join',
              'Reading cost estimates. (Typical.)',
              'Size estimates', 'Join strategies depend on size estimates; explain cost shows them, and stats, hints or AQE fix wrong ones', [b1, b2, b3, b4, b5],
              ['Slow join.', 'Estimate.', 'No stats.', 'Fix.', 'Broadcast.'],
              hid='scenario-estimates')
u1 = (t(180, 22, 'Filter on a UDF', 9.4, bold=True) + t(180, 56, 'where(is_premium(city))', 8.4, 'ink', mono=True) + cap('Reads the whole table.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'Plan: DataFilters []', 9.4, bold=True) + t(180, 56, 'ArrowEvalPython above scan', 8.4, 'ink2') + cap('Our Step 6.', '', 'red', y=150, h=34))
u3 = (t(180, 22, 'Rewrite as expression', 9.4, bold=True) + t(180, 56, 'col("city").isin(PREMIUM)', 8.4, 'ink', mono=True) + cap('Catalyst sees it.', '', 'green', y=150, h=34))
u4 = (t(180, 22, 'Filter pushed to Parquet', 9.4, bold=True) + t(180, 56, 'In(city, [...]) in PushedFilters', 8.2, 'ink2') + cap('Row groups skipped.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Rule of thumb', 9.4, 'acc', bold=True) + t(180, 56, 'no UDFs in filters and join keys', 8.4, 'ink2') + cap('Keep them visible.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'A filter the optimizer could not see',
              'UDFs and pushdown. (Behaviour from our lab.)',
              'Opaque filters', 'UDF predicates are not pushed down; express filters with built-ins so Catalyst can push them', [u1, u2, u3, u4, u5],
              ['UDF filter.', 'No pushdown.', 'Expression.', 'Pushed.', 'Rule.'],
              hid='scenario-opaque')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>What Spark really runs</h2>
  <p>Left: real outputs. Right: the plans.</p>
''' + two + '''
  <p>Three live scenarios follow: rewriting code Catalyst rewrites anyway, a wrong join choice, and a filter the optimizer could not see.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Reading plans at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'PR', 12, 'blue', bold=True) + t(60, 58, 'reviews', 7.4, 'ink2'),
    '1. Plan reviews',
    'Teams attach explain("formatted") output to pull requests for heavy queries.',
    ['Query', '*explain', 'Review']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'tuning', 11, 'green', bold=True) + t(60, 58, 'joins', 7.4, 'ink2'),
    '2. Join tuning',
    'Engineers check join strategies and Exchanges before changing cluster sizes.',
    ['Slow job', '*read plan', 'Right fix']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'lake', 12, 'violet', bold=True) + t(60, 58, 'pushdown', 7.4, 'ink2'),
    '3. Lake layout checks',
    'PushedFilters and ReadSchema confirm that partitioning and sorting are used.',
    ['Table', '*PushedFilters', 'Layout fix']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'stats', 12, 'acc', bold=True) + t(60, 58, 'CBO', 7.4, 'ink2'),
    '4. Cost-based optimization',
    'With ANALYZE stats and spark.sql.cbo.enabled, Catalyst reorders multi-way joins.',
    ['Stats', '*CBO', 'Join order']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'UDF', 12, 'acc', bold=True) + t(60, 58, 'audit', 7.4, 'ink2'),
    '5. UDF audits',
    'Searching plans for EvalPython nodes finds UDFs worth replacing.',
    ['Plans', '*EvalPython?', 'Rewrite list']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> plans in <a href="../../04-dataframes/01-sparksession-and-dataframes/">4.1</a>, join strategies in <a href="../../06-transformations/02-joins/">6.2</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
