import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='07-spark-sql', lesson='03-catalyst-and-explain', n='7.3',
    module_label='Module 7 · Spark SQL',
    title='Catalyst and explain',
    desc='The Catalyst optimizer read through explain() in PySpark 4.3.0: parsed, analyzed, optimized and physical plans of a 5M-order join, filters pushed below the join and into Parquet (5 PushedFilters), constant folding of (1 + 1) + 798 into 800, column pruning, a broadcast join chosen by size, explain formatted and cost, whole-stage code generation with 2 generated stages, identical plans for "bad" and "good" code, and a UDF filter Catalyst could not push.',
    og_desc='We wrote a query badly and well: Catalyst produced the identical plan. Reading Spark’s four plans with explain(), step by step.',
    minutes=32, level='Intermediate → Advanced',
    lead='Every DataFrame and SQL query passes through <b>Catalyst</b>. This lesson reads all four plans of a real join, shows the rewrites the optimizer makes (pushdown, pruning, constant folding, join strategy), whole-stage code generation, and the limits of optimization. <b>All outputs are real</b> (PySpark 4.3.0).',
    chips=['PySpark 4.3.0', 'Four plans read', 'Same plan, two styles', 'Runs in your browser (Python)'],
)

MAIN = '''# A tiny optimizer: constant folding + predicate pushdown (toy model)
plan = ["scan orders", "scan customers", "join", "filter status = DELIVERED",
        "filter plan = Gold", "filter amount > 1 + 1 + 798"]

def optimize(plan):
    out, pushed = [], {"orders": [], "customers": []}
    for step in plan:
        if step.startswith("filter"):
            cond = step.replace("1 + 1 + 798", str(1 + 1 + 798))     # constant folding
            side = "customers" if "plan" in cond else "orders"     # which table owns the column
            pushed[side].append(cond)
        elif step != "join":
            out.append(step)
    return pushed, out + ["join"]

pushed, rest = optimize(plan)
print("pushed below join:", pushed)
print("remaining:", rest)
'''
RUN = dict(
    heading='Run the code: a toy optimizer',
    intro='<p>A simplified model of Step 2’s rewrites. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('            cond = step.replace("1 + 1 + 798", str(1 + 1 + 798))     # constant folding', 'Catalyst turned ((1 + 1) + 798) into 800.'),
        ('            side = "customers" if "plan" in cond else "orders"     # which table owns the column', 'Each filter goes to the side whose columns it uses.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Add a filter on city and see where it goes.', code=None),
        dict(label='2 · Predict first: columns read', hint='<b>Predict first:</b> which order columns are needed for the final select and filters?',
             code='''select = {"order_id", "amount"}
filters = {"status", "amount"}
join_key = {"customer_id"}
print(sorted(select | filters | join_key))
'''),
        dict(label='3 · Read a plan bottom-up', hint='Reverse the operator list.',
             code='''plan = ["Project", "BroadcastHashJoin", "Filter", "FileScan parquet"]
print(" -> ".join(reversed(plan)))
'''),
        dict(label='4 · Broadcast decision', hint='Compare an estimate with the threshold.',
             code='''threshold = 10 * 1024 * 1024
for est in (60_000, 2_000_000_000):
    print(est, "->", "broadcast" if est <= threshold else "sort-merge")
'''),
        dict(label='5 · Spot the error', hint='This filter uses a UDF.', expect='error',
             code='''plan_line = "FileScan parquet … DataFilters: [], PushedFilters: []"
assert "PushedFilters: []" not in plan_line, "the UDF filter was not pushed: use a built-in expression"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: explain',
    intro='<p>In the <code>pyspark</code> shell. <b>Outputs are real</b> (PySpark 4.3.0).</p>',
    items=[
        dict(title='1 · Constant folding', cmd='o.where(F.col("amount") > F.lit(1) + F.lit(1) + F.lit(798))._jdf.queryExecution().optimizedPlan().toString().splitlines()[0]', file='pyspark',
             output='Filter (isnotnull(amount#4) AND (amount#4 > 800))', note='Folded before running.'),
        dict(title='2 · Codegen', cmd='s.explain(mode="codegen")   # with AQE off', file='pyspark',
             output='Found 2 WholeStageCodegen subtrees.', note='One per side of the shuffle.'),
        dict(title='3 · SQL', cmd='spark.sql("EXPLAIN FORMATTED SELECT amount FROM orders WHERE city = \'Pune\'").first()[0][:40]', file='pyspark',
             output="'== Physical Plan ==\\n* Project (4)\\n+- * F'", note='Same modes as explain().'),
    ],
)

TRACE = dict(
    heading='Which side does a filter belong to?',
    intro='<p>Follow how each predicate is assigned by its columns.</p>',
    code='''columns = {"orders": {"status", "amount", "customer_id"}, "customers": {"plan", "name", "customer_id"}}
filters = [("status = DELIVERED", {"status"}), ("plan = Gold", {"plan"}), ("amount > 800", {"amount"})]
for text, cols in filters:
    side = [t for t, c in columns.items() if cols <= c][0]
    print(f"{text:20} -> {side}")
''',
    notes={4: 'Pushdown :: A filter using only one side’s columns moves below the join.'},
)

WORKED_INTRO = 'Three plan-reading tasks.'
EXAMPLES = [
    dict(level='b', tag='explain · basics', title='Is my filter pushed?',
         problem='<p>Check that a city filter reaches Parquet.</p>',
         inp='spark.read.parquet(...).where(city = Pune)',
         approach=['explain("formatted").', 'Find the Scan.', 'Read PushedFilters.'],
         code='''line = "PushedFilters: [IsNotNull(city), EqualTo(city,Pune)]"
print("pushed" if "EqualTo(city,Pune)" in line else "not pushed")
''', notes={1: 'Formatted :: Each operator’s details on its own lines.'},
         tryit='Step 4.'),
    dict(level='i', tag='explain · joins', title='Why no broadcast?',
         problem='<p>A small dimension is joined with sort-merge.</p>',
         inp='plan shows SortMergeJoin',
         approach=['explain("cost") for sizeInBytes.', 'Compare with 10 MB.', 'Stats, hint or AQE.'],
         code='''est_mib, limit_mib = 2048, 10
print("broadcast" if est_mib <= limit_mib else "sort-merge: estimate too big, check statistics")
''', notes={1: 'Estimate :: Without stats, file size is used.'},
         tryit='Scenario 2.'),
    dict(level='a', tag='explain · design', title='Make a filter optimizable',
         problem='<p>Replace a UDF filter with something Catalyst can push.</p>',
         inp='is_premium(city) UDF',
         approach=['Express as isin().', 'Check PushedFilters.', 'Measure rows read.'],
         code='''PREMIUM = ["Mumbai", "Bengaluru"]
print(f'F.col("city").isin({PREMIUM})  -> PushedFilters: In(city, {PREMIUM})')
''', notes={1: 'Visible :: Built-in predicates can be pushed.'},
         tryit='Step 6.'),
]

QUIZ = mix([
    dict(q='Beginner: Which mode shows all four plans?', options=['simple', 'extended', 'cost', 'codegen'], answer=1,
         why='Parsed, analyzed, optimized, physical.'),
    dict(q='Beginner: Which phase resolves column names?', options=['Parsing', 'Analysis', 'Physical planning', 'Codegen'], answer=1,
         why='Typos fail here.'),
    dict(q='Beginner: What is predicate pushdown?', options=['Sorting', 'Moving filters toward or into the data source', 'Caching', 'Broadcasting'], answer=1,
         why='Filters below the join and in the scan.'),
    dict(q='Intermediate: What became of (1 + 1) + 798?', options=['Computed per row', '800 at optimization', 'An error', 'A string'], answer=1,
         why='Constant folding.'),
    dict(q='Intermediate: What does *(1) mean in a plan?', options=['Stage 1 of the job', 'Whole-stage codegen stage 1', 'Partition 1', 'Priority'], answer=1,
         why='Fused generated code.'),
    dict(q='Intermediate: “Bad” and “good” query styles gave…', options=['Different plans', 'Identical optimized plans', 'Errors', 'Different results'], answer=1,
         why='Catalyst rewrote both.'),
    dict(q='Advanced: Why might explain() hide codegen markers?', options=['Bug', 'AQE shows the initial plan before running', 'Small data', 'Python'], answer=1,
         why='isFinalPlan=false.'),
    dict(q='Advanced: What does Catalyst NOT optimize?', options=['Filters', 'Constant expressions', 'Python UDF internals', 'Join order with stats'], answer=2,
         why='Black box.'),
])

REVISION = [
    'Catalyst: parsed → analyzed → optimized → physical, then whole-stage codegen.',
    '<code>explain(mode=…)</code>: simple, extended, formatted, cost, codegen; SQL <code>EXPLAIN …</code>.',
    'Rewrites: predicate pushdown (below joins, into scans), column pruning, constant folding (1+1+798 → 800).',
    'Physical: strategies from size estimates (broadcast for the 2,000-row table).',
    'Formatted: PushedFilters and ReadSchema per scan; cost: sizeInBytes.',
    'Two code styles → identical optimized plan: write clear code.',
    'UDF filters are not pushed; AQE shows the initial plan before execution.',
]
FAQ = [
    ('Is the order of my where/select calls important?', 'Usually not; Catalyst reorders filters and projections. It matters for things it cannot see through, like UDFs or caching points.'),
    ('What is CBO?', 'Cost-based optimization: with ANALYZE statistics and spark.sql.cbo.enabled=true, Catalyst estimates cardinalities to reorder multi-way joins.'),
    ('Can I see the plan that actually ran?', 'Yes: the SQL / DataFrame tab of the Spark UI, or explain() after an action (isFinalPlan=true).'),
    ('Can Catalyst be extended?', 'Yes, with custom rules and strategies via SparkSessionExtensions (mostly in Scala); data sources can implement pushdown interfaces.'),
    ('Does caching affect plans?', 'Yes: cached DataFrames appear as InMemoryRelation scans and later queries reuse them.'),
]

PRACTICE_INTRO = 'Programs about plans and optimizer rules.'
PROBLEMS = [
    dict(level='easy', title='Fold', stmt='Fold a constant expression.', inp='(1 + 1) + 798',
         code='''print((1 + 1) + 798)
''', explain='Done once, not per row.'),
    dict(level='easy', title='Columns', stmt='Columns read out of six.', inp='4 needed',
         code='''print(f"{4 / 6:.0%} of columns")
''', explain='Column pruning.'),
    dict(level='easy', title='Size shrink', stmt='Size after projection.', inp='34.6 → 6.1 MiB',
         code='''print(f"{6.1 / 34.6:.0%}")
''', explain='From explain(cost).'),
    dict(level='medium', title='Filter sides', stmt='Assign filters to tables by column.', inp='filters',
         code='''owner = {"status": "orders", "plan": "customers", "amount": "orders"}
print({c: owner[c] for c in ("status", "plan", "amount")})
''', explain='Pushdown below the join.'),
    dict(level='medium', title='Plan order', stmt='Execution order of a plan.', inp='printed top-down',
         code='''printed = ["Project", "Join", "Filter", "Scan"]
print(printed[::-1])
''', explain='Bottom-up.'),
    dict(level='medium', title='Exchanges', stmt='Count shuffles in a plan.', inp='plan text',
         code='''plan = "Sort <- Exchange <- HashAggregate <- Exchange <- HashAggregate <- Scan"
print(plan.count("Exchange"))
''', explain='Each Exchange is a shuffle.'),
    dict(level='business', title='Review time saved', stmt='Hours saved by checking plans instead of rewriting.', inp='10 rewrites × 1.5 h',
         code='''print(10 * 1.5, "hours")
''', explain='Identical plans need no rewrite.'),
    dict(level='business', title='Scan saving', stmt='Data skipped by pushdown on a 1 TB table.', inp='filter keeps 5%',
         code='''print(1000 * 0.95, "GB not read")
''', explain='With good layout.'),
]

SCN_INTRO = 'Catalyst questions separate users of Spark from engineers who tune it.'
SCENARIOS = (
    scn('Any company · Spark', 'Fresher', '“What is Catalyst?”',
        'Explain the Catalyst optimizer.',
        'phases?',
        '<p>Spark SQL’s optimizer. It parses the query, analyzes it against the catalog, applies rules such as predicate pushdown, column pruning and constant folding, then chooses physical operators like broadcast joins; whole-stage codegen compiles the plan. explain() shows each phase.</p>', 'Confusing it with Tungsten only.') +
    scn('Data engineering', 'Mid-level', 'Read a plan',
        'How do you check if a filter is pushed to Parquet?',
        'explain skills?',
        '''<ul>
          <li>explain("formatted") and find the Scan operator.</li>
          <li>Check PushedFilters and ReadSchema.</li>
          <li>Empty PushedFilters usually means a UDF or unsupported expression.</li>
        </ul>''', 'Guessing from run times.') +
    scn('Data engineering', 'Mid-level', 'Rewrite for performance?',
        'A colleague wants to reorder filters and selects for speed.',
        'trust but verify?',
        '''<ol>
          <li>Compare optimized plans first; often identical.</li>
          <li>Focus on things Catalyst cannot fix: UDFs, data layout, skew, missing stats.</li>
          <li>Keep code readable.</li>
        </ol>''', 'Micro-optimising order of where calls.') +
    scn('Platform', 'Senior', 'Bad join choices',
        'Large shuffles for joins with small tables.',
        'estimates and strategies?',
        '''<ul>
          <li>explain("cost") for size estimates.</li>
          <li>ANALYZE tables; enable CBO; hints where needed.</li>
          <li>Rely on AQE to correct at run time (7.4).</li>
        </ul>''', 'Raising autoBroadcastJoinThreshold to 10 GB.')
)
