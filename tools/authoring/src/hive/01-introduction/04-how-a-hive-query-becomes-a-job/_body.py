import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from hivekit import *

QUERY = ['SELECT city, SUM(amount) AS total', 'FROM orders', 'WHERE amount > 100', 'GROUP BY city', 'ORDER BY total DESC;']

# ---------------------------------------------------------------- story
sc = (box(14, 18, 150, 100, 'card') + t(89, 34, 'What Kabir writes', 9.4, bold=True) +
      ''.join(t(24, 52 + k * 13, s, 7.8, anchor='start', mono=True) for k, s in enumerate(QUERY)) +
      arrow(170, 68, 214, 68, 'ink3', 2.2) +
      box(220, 18, 200, 100, 'acc') + t(320, 34, 'What Hive builds', 9.4, bold=True) +
      ''.join(chip(232 + k * 62, 50, nm, col, w=56, h=18, size=7.8) for k, (nm, col) in enumerate([('Parse', 'blue'), ('Analyse', 'violet'), ('Optimise', 'green')])) +
      ''.join(chip(250 + k * 80, 78, nm, col, w=72, h=18, size=7.8) for k, (nm, col) in enumerate([('Map 1', 'acc'), ('Reducer 2', 'blue')])) +
      t(320, 108, '→ Tez job (a DAG)', 8, 'ink2') + arrow(426, 68, 470, 68, 'ink3', 2.2) +
      box(476, 18, 150, 100, 'green') + t(551, 34, 'What the cluster runs', 9.4, bold=True) +
      ''.join(fill(488 + (k % 6) * 22, 48 + (k // 6) * 18, 18, 14, 'acc', rx=3) for k in range(12)) + t(551, 108, '16 + 4 + 1 tasks', 8, 'ink2'))
scene_svg = scene('A five-line SQL query becomes a parse tree, an optimised plan, a Tez graph of tasks and finally many tasks running in containers.', sc,
                  'Five lines of SQL in, <tspan font-weight="700" class="s-acc">twenty-one tasks</tspan> out.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Why did my five lines turn into twenty-one tasks?”</h2>
  <div class="story">
    <p class="narration">Kabir runs his first real Hive report: total order value per city, only for orders above Rs 100, biggest city first. It finishes in 19 seconds. Out of curiosity he scrolls up and sees the progress table Hive printed: <code>Map 1: 16/16</code>, <code>Reducer 2: 4/4</code>, <code>Reducer 3: 1/1</code>. Twenty-one tasks for five lines of SQL.</p>

{scene_svg}

K> Sir, who decided on 16, 4 and 1? I never wrote any of that.
A> Hive did. Between the moment you press Enter and the first container starting, a small factory runs inside HiveServer2. Think of a <b>restaurant order slip</b>: you write “one thali, no onion”. The kitchen turns it into stations: one cook chops, another fries, one plates. You never see the stations, but without them nothing is cooked.
R> And the factory has steps?
A> Five: <b>parse</b> the text into a tree, <b>analyse</b> it against the metastore, <b>optimise</b> the plan, turn it into a <b>graph of tasks</b>, and <b>execute</b> that graph on YARN. Today you will see every step. You will also learn the one command, <code>EXPLAIN</code>, that lets you read the plan <i>before</i> spending cluster time.
K> So I can tell why a query is slow without running it?
A> Very often, yes. That is the skill that separates people who use Hive from people who tune it.
  </div>
</section>
'''

# ---------------------------------------------------------------- definition
lv = '''
LEVELS> From SQL to tasks at three levels
L1> A restaurant order
      <ul>
        <li><b>You write the order</b> (the SQL). It says <i>what</i> you want, not how to cook it.</li>
        <li><b>The waiter checks it</b> (parse + analyse): are the dishes on the menu? That is the metastore check.</li>
        <li><b>The head chef improves the plan</b> (optimise): “peel only the vegetables we need, and start the sauce while the rice boils”.</li>
        <li><b>Stations are assigned</b> (the DAG): one station per kind of work, in order.</li>
        <li><b>Cooks work in parallel</b> (tasks in containers), and the plate comes back to you.</li>
      </ul>
L2> The five phases
      <ul>
        <li><b>1 · Parse:</b> the HiveQL text becomes an <b>abstract syntax tree (AST)</b>. Syntax errors (a missing comma) are reported here.</li>
        <li><b>2 · Semantic analysis:</b> tables, columns and types are checked with the metastore, and the AST becomes a <b>logical plan</b>: a tree of <b>operators</b> such as TableScan, Filter, Select, Group By, Reduce Sink and File Sink.</li>
        <li><b>3 · Optimisation:</b> rule-based rewrites (push filters down, read only needed columns, skip partitions, fold constants) and <b>cost-based optimisation</b> (choose join order and join type using statistics), done with Apache Calcite.</li>
        <li><b>4 · Physical plan:</b> the operator tree is cut at every <b>Reduce Sink</b> (where data must be shuffled) into <b>vertices</b>. Vertices joined by edges form a <b>DAG</b>: <code>Map 1 → Reducer 2 → Reducer 3</code>.</li>
        <li><b>5 · Execute:</b> the Tez AM runs in YARN, starts tasks in containers (one task per input split in a map vertex, a chosen number in reducer vertices), moves data along the edges and writes the result.</li>
      </ul>
L3> What the optimiser and engine really do
      <ul>
        <li><b>Predicate pushdown:</b> the <code>WHERE</code> filter is moved as close to the data as possible; with ORC/Parquet whole stripes or row groups are skipped using min/max statistics.</li>
        <li><b>Column pruning:</b> only columns used by the query are read; with a columnar format the others are never touched.</li>
        <li><b>Partial (map-side) aggregation:</b> each map task first aggregates its own rows (<code>mode: hash</code>); the reducer finishes (<code>mode: mergepartial</code>). The shuffle then carries a few rows per city instead of millions.</li>
        <li><b>Join strategies:</b> a <b>shuffle join</b> repartitions both tables by key; a <b>map (broadcast) join</b> sends a small table to every task and needs no shuffle. Hive chooses automatically when a table is small enough (<code>hive.auto.convert.join</code>).</li>
        <li><b>ORDER BY is a total sort:</b> it needs a single reducer (or merge) at the end, which can be a bottleneck on huge data; <code>SORT BY</code> and <code>DISTRIBUTE BY</code> sort per reducer only.</li>
        <li><b>Tez vs MapReduce:</b> MapReduce ran one job per stage and wrote every intermediate result to HDFS. Tez runs the whole DAG as one job and streams data between vertices, usually with far fewer disk writes. <b>Vectorised execution</b> processes batches of rows at a time.</li>
        <li><b>Reducer parallelism</b> is estimated from input size (for example bytes per reducer) and can be adjusted automatically at run time; the “4” in our story came from such an estimate.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Query compilation and execution in Hive</h2>
''' + def_block(
    '<b>Query compilation in Hive</b> is the process by which HiveServer2 converts a HiveQL statement into an executable plan in five phases: <b>parsing</b> into an abstract syntax tree; <b>semantic analysis</b> against the metastore, producing a logical plan of operators; <b>optimisation</b> by rule-based transformations and a cost-based optimiser (Apache Calcite); generation of a <b>physical plan</b>, a directed acyclic graph (DAG) of vertices connected by edges at each shuffle boundary; and <b>execution</b> of that DAG by an engine such as <b>Apache Tez</b> as tasks in YARN containers. The plan can be inspected with the <b>EXPLAIN</b> statement without running the query.',
    'Hive reads your SQL, checks it, rewrites it to do less work, cuts it into stages at every place where data must be regrouped (the <b>shuffle</b>), and hands those stages to YARN to run as many small parallel tasks. <code>EXPLAIN</code> shows the stages before anything runs.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('AST', 'Abstract syntax tree: the query text as a tree of clauses (SELECT, FROM, WHERE, …).'),
    ('Operator', 'One step of a plan: TableScan, Filter, Select, Group By, Join, Reduce Sink, File Sink.'),
    ('Vertex', 'A Tez stage (“Map 1”, “Reducer 2”): many identical tasks working on different pieces of data.'),
    ('Edge', 'A data connection between vertices. A <code>SIMPLE_EDGE</code> is a shuffle; a <code>BROADCAST_EDGE</code> sends a small table to all tasks.'),
    ('Reduce Sink', 'The operator that ends a vertex: it partitions rows by key and sends them over the shuffle.'),
    ('Predicate pushdown', 'Applying a filter as early as possible, ideally inside the file reader, to avoid reading rows at all.'),
    ('Cost-based optimiser', 'Chooses among equivalent plans using table statistics (row counts, distinct values).'),
    ('EXPLAIN', 'A statement that prints the plan of a query without executing it.'),
]) + '''

  <h3>Clause order: how SQL is read versus how it is evaluated</h3>
''' + table(['You write (in this order)', 'Hive evaluates (logical order)', 'Where it shows in the plan'], [
    ['<code>SELECT city, SUM(amount)</code>', '4th: choose and compute output columns', 'Select / Group By operators'],
    ['<code>FROM orders</code>', '1st: find and scan the table', 'TableScan in Map 1'],
    ['<code>WHERE amount &gt; 100</code>', '2nd: filter individual rows', 'Filter Operator in Map 1 (pushed down)'],
    ['<code>GROUP BY city</code>', '3rd: group rows by key', 'Group By (hash) in Map 1, final Group By in Reducer 2'],
    ['<code>ORDER BY total DESC</code>', '5th: sort the result', 'Reducer 3, usually a single reducer'],
    ['<code>LIMIT 10</code>', '6th: keep the first rows', 'Limit operator at the end'],
], minw=620) + lv + '''
EXAM> “Explain how a Hive query is executed.” Give the five phases in order (parse → semantic analysis with metastore → logical plan and optimisation → physical plan / DAG → execution on Tez/YARN), name one optimisation (predicate pushdown or partial aggregation) and mention <code>EXPLAIN</code>. A neat flow diagram earns the marks.
</section>
'''

# ---------------------------------------------------------------- types
types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Plans, engines and the EXPLAIN family</h2>
''' + cards([
    ('Tez (default)', 'One DAG per query, data streamed between vertices, container re-use, vectorised execution. The standard engine in modern Hive.', 'hive.execution.engine=tez'),
    ('MapReduce (deprecated)', 'One MapReduce job per stage with intermediate results in HDFS. You will still meet it in old clusters and old tutorials.', 'Legacy'),
    ('Hive on Spark', 'Optional engine that runs the plan on Spark. Rare today; most teams use Spark SQL directly instead.', 'Rare'),
    ('LLAP', 'Long-lived daemons that cache data and keep code warm, so short queries skip container start-up. Works with Tez.', 'Interactive'),
]) + '''

  <h3>The EXPLAIN family</h3>
''' + table(['Statement', 'What it shows', 'Use it to…'], [
    ['<code>EXPLAIN query</code>', 'Stage dependencies and the operator tree of every vertex', 'Check the number of stages and the join type'],
    ['<code>EXPLAIN EXTENDED query</code>', 'Adds file paths, partitions read and more detail', 'Verify partition pruning and input paths'],
    ['<code>EXPLAIN DEPENDENCY query</code>', 'The tables and partitions the query reads (JSON)', 'Audit lineage or find unexpected inputs'],
    ['<code>EXPLAIN CBO query</code>', 'The plan the cost-based optimiser chose', 'Understand join ordering decisions'],
    ['<code>EXPLAIN ANALYZE query</code>', 'Runs the query and shows actual versus estimated rows', 'Find where the estimates were wrong'],
], minw=640) + '''
  <h3>Read an EXPLAIN in four questions</h3>
''' + table(['Ask', 'Look for', 'Red flag'], [
    ['How many vertices?', '<code>Edges:</code> and <code>Map 1</code>, <code>Reducer 2</code> …', 'Many reducer stages for a simple query'],
    ['Is the filter early?', '<code>Filter Operator</code> inside <code>Map 1</code>, right after <code>TableScan</code>', 'Filter only in a reducer'],
    ['Are partitions pruned?', '<code>EXPLAIN EXTENDED</code> lists only the needed partitions', 'All partitions listed'],
    ['How do joins run?', '<code>BROADCAST_EDGE</code> (map join) versus <code>SIMPLE_EDGE</code> (shuffle join)', 'A huge shuffle join where one side is small'],
], minw=560) + '''
TIP> Run <code>EXPLAIN</code> on every new report <i>before</i> you schedule it. It costs milliseconds, uses no containers, and often shows a missing partition filter or an avoidable shuffle that would have burned hours of cluster time.
</section>
'''

# ---------------------------------------------------------------- steps
c1 = '''query = "SELECT city, SUM(amount) FROM orders WHERE amount > 100 GROUP BY city ORDER BY 2 DESC"
words = ["SELECT", "FROM", "WHERE", "GROUP BY", "ORDER BY"]
parts, rest = {}, query
for w in reversed(words):
    head, _, tail = rest.partition(w)
    if tail:
        parts[w], rest = tail.strip(), head
print(parts)'''
c2 = '''plan = [("TableScan", "orders"), ("Filter", "amount > 100"), ("Select", "city, amount"),
        ("GroupBy(hash)", "sum(amount) by city"), ("ReduceSink", "key = city"),
        ("GroupBy(merge)", "sum by city"), ("ReduceSink", "sort by total desc"), ("FileSink", "result")]
for op, arg in plan:
    print(f"{op:15}{arg}")'''
c3 = '''plan = ["TableScan", "Filter", "Select", "GroupBy(hash)", "ReduceSink",
        "GroupBy(merge)", "Select", "ReduceSink", "Select", "FileSink"]
vertices, current = [], []
for op in plan:
    current.append(op)
    if op == "ReduceSink":
        vertices.append(current); current = []
vertices.append(current)
for i, v in enumerate(vertices, 1):
    print(f"vertex {i}:", " -> ".join(v))'''
c4 = '''rows = 12_000_000
cities = 38
maps = 16
print("shuffle rows without map-side aggregation:", rows)
print("shuffle rows with map-side aggregation  :", maps * cities)'''
c5 = '''import math
input_gb, bytes_per_reducer_gb = 1.8, 0.5
reducers = max(1, math.ceil(input_gb / bytes_per_reducer_gb))
print("estimated reducers:", reducers)'''
steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Following one query through the five phases</h2>
''' + stepper([
    ('Phase 1 · Parse the text',
     code('python', 'parse.py', c1, run_code(c1)),
     'Hive’s real parser (built with ANTLR) produces an abstract syntax tree. This toy splits the clauses to show the idea: a query is a set of named parts. A missing comma or misspelt keyword fails here with a “ParseException”.'),
    ('Phase 2 · Analyse and build the operator tree',
     code('python', 'operators.py', c2, run_code(c2)),
     'The analyser asks the metastore about <code>orders</code>, confirms <code>city</code> and <code>amount</code> exist, and writes the query as a chain of operators. Note that <b>Filter comes before Group By</b>, although SQL text puts WHERE after FROM and SELECT first.'),
    ('Phase 3 · Optimise',
     '<p>The optimiser rewrites the tree. Three rewrites matter in this query: the <b>filter is pushed</b> into the scan, <b>only two columns are read</b> (<code>city</code>, <code>amount</code>), and a <b>partial aggregation</b> is added before the shuffle (step 4).</p>',
     'None of these change the answer; all of them reduce work. The cost-based optimiser also decides join order and join type from table statistics, which is why <code>ANALYZE TABLE</code> matters.'),
    ('Phase 4 · Cut into vertices at every shuffle',
     code('python', 'vertices.py', c3, run_code(c3)),
     'Every <b>ReduceSink</b> ends a vertex, because data must be regrouped across machines there. Our query has three: <code>Map 1</code> (scan, filter, partial aggregation), <code>Reducer 2</code> (final aggregation) and <code>Reducer 3</code> (global sort).'),
    ('Why the partial aggregation matters',
     code('python', 'combiner.py', c4, run_code(c4)),
     'Without it, 12 million rows would cross the network. With it each of 16 map tasks sends at most 38 rows (one per city): 608 rows. Hive calls it <code>mode: hash</code> in <code>EXPLAIN</code>.'),
    ('Phase 5 · Execute on Tez: how many tasks?',
     code('python', 'parallelism.py', c5, run_code(c5)),
     'A map vertex gets one task per input split (16 here), reducer vertices get a number estimated from data size, and the final sort uses one. YARN grants containers and Tez runs them. Total in our story: 16 + 4 + 1 = 21 tasks.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
def stagebar(active):
    names = ['Parse', 'Analyse', 'Optimise', 'Plan', 'Run']
    o = ''
    for k, n in enumerate(names):
        o += chip(8 + k * 70, 8, n, 'acc' if k == active else 'grey', w=64, h=20, size=8)
        if k < 4:
            o += t(8 + k * 70 + 67, 22, '›', 9, 'ink3')
    return o


def qlines(x=22, y=62, hl=None):
    o = ''
    for k, s in enumerate(QUERY):
        o += t(x, y + k * 13, s, 8.4, 'acc' if hl == k else 'ink', anchor='start', mono=True)
    return o


def ops(row_y, names, color, x0=8, w=64, label=''):
    o = ''
    for k, nm in enumerate(names):
        o += chip(x0 + k * (w + 6), row_y, nm, color, w=w, h=18, size=7.2)
        if k < len(names) - 1:
            o += t(x0 + k * (w + 6) + w + 3, row_y + 12, '›', 8, 'ink3')
    return o


def vtx(x, y, w, name, n, tone):
    return label_box(x, y, w, 36, [name, f'{n} task' + ('s' if n != 1 else '')], tone, 8.2)


def tasks(x, y, n, color, cols=8):
    o = ''
    for k in range(n):
        o += fill(x + (k % cols) * 14, y + (k // cols) * 12, 11, 9, color, rx=2)
    return o


B1 = [
    stagebar(0) + qlines() + t(180, 150, 'Text: five lines of SQL', 9, 'ink2') + t(180, 170, 'Parser reads keywords and builds a tree', 8.4, 'ink2'),
    stagebar(0) + t(180, 52, 'AST (abstract syntax tree)', 9, bold=True) + box(120, 62, 120, 20, 'blue') + t(180, 75, 'QUERY', 8, bold=True) +
    ''.join(box(10 + k * 70, 104, 64, 20, 'card') + t(42 + k * 70, 117, nm, 7.4, bold=True) + f'<path d="M180 82L{42 + k * 70} 104" class="s-line"/>' for k, nm in enumerate(['FROM', 'SELECT', 'WHERE', 'GROUP BY', 'ORDER BY'])) +
    t(180, 150, 'Syntax errors are reported here', 8.8, 'ink2'),
    stagebar(1) + t(180, 46, 'Logical plan: a chain of operators', 9, bold=True) + ops(56, ['TableScan', 'Filter', 'Select', 'GroupBy', 'ReduceSink'], 'blue', w=58) +
    ops(86, ['GroupBy', 'Select', 'ReduceSink'], 'violet', x0=8, w=58) + ops(116, ['Select', 'FileSink'], 'green', x0=8, w=58) + t(180, 156, 'Tables and columns checked against the metastore', 8.6, 'ink2'),
    stagebar(2) + t(180, 46, 'Optimised: less work, same answer', 9, 'green', bold=True) +
    box(10, 56, 340, 28, 'green') + t(180, 68, 'Filter pushed into the scan', 8.6, bold=True) + t(180, 79, 'amount > 100 applied while reading', 7.6, 'ink2') +
    box(10, 90, 340, 28, 'green') + t(180, 102, 'Column pruning', 8.6, bold=True) + t(180, 113, 'read only city and amount (2 of 10 columns)', 7.6, 'ink2') +
    box(10, 124, 340, 28, 'green') + t(180, 136, 'Partial aggregation before the shuffle', 8.6, bold=True) + t(180, 147, 'each map task sends at most one row per city', 7.6, 'ink2'),
    stagebar(3) + t(180, 46, 'Physical plan: a DAG of vertices', 9, bold=True) + vtx(10, 70, 96, 'Map 1', 16, 'acc') + vtx(132, 70, 96, 'Reducer 2', 4, 'blue') + vtx(254, 70, 96, 'Reducer 3', 1, 'violet') +
    arrow(108, 88, 130, 88, 'red', 2) + arrow(230, 88, 252, 88, 'red', 2) + t(119, 66, 'shuffle', 7.2, 'red', bold=True) + t(241, 66, 'shuffle', 7.2, 'red', bold=True) +
    t(180, 132, 'Cut at every Reduce Sink · one task per split in Map 1', 8.4, 'ink2'),
    stagebar(4) + t(180, 46, 'Tez runs the DAG in YARN containers', 9, bold=True) + vtx(10, 56, 96, 'Map 1', 16, 'acc') + tasks(12, 98, 16, 'var(--track)') +
    vtx(132, 56, 96, 'Reducer 2', 4, 'blue') + tasks(134, 98, 4, 'var(--blue)', 4) + vtx(254, 56, 96, 'Reducer 3', 1, 'violet') + tasks(256, 98, 1, 'var(--violet)', 1) +
    t(180, 150, '21 tasks = 16 + 4 + 1, each in a container', 8.6, 'ink2'),
    stagebar(4) + t(180, 60, 'Result written, then streamed to the client', 9, 'green', bold=True) + box(80, 76, 200, 66, 'green') +
    t(180, 94, 'Mumbai   450', 9, mono=True) + t(180, 110, 'Pune     400', 9, mono=True) + t(180, 126, 'Thane    150', 9, mono=True) + t(180, 166, 'Intermediate data is discarded', 8.4, 'ink2'),
]
G, W, Y = '#9FD3B8', '#EDEBE3', '#F5C77E'
def term(lines):
    o = '<rect x="14" y="14" width="332" height="196" rx="8" class="s-board"/><text x="26" y="30" font-size="9" class="mono" style="fill:#7F8C86">beeline (illustrative)</text>'
    for k, (txt, col) in enumerate(lines):
        o += f'<text x="26" y="{50 + k * 14}" font-size="8" class="mono" style="fill:{col}">{txt}</text>'
    return o
see = [
    term([('SELECT city, SUM(amount) AS total', W), ('FROM orders WHERE amount > 100', W), ('GROUP BY city ORDER BY total DESC;', W)]),
    term([('INFO : Compiling command(queryId=…)', G), ('(a typo here would say:', Y), (' ParseException line 2:8 …)', Y)]),
    term([('INFO : Semantic Analysis Completed', G), ('(an unknown column would say:', Y), (' Invalid column reference)', Y)]),
    term([('INFO : Semantic Analysis Completed', G), ('INFO : Completed compiling command', G), ('INFO : Executing command(queryId=…)', G)]),
    term([('EXPLAIN shows (trimmed):', W), ('Edges:', W), ('  Reducer 2 &lt;- Map 1 (SIMPLE_EDGE)', G), ('  Reducer 3 &lt;- Reducer 2 (SIMPLE_EDGE)', G)]),
    term([('Map 1 ........ SUCCEEDED   16', G), ('Reducer 2 .... SUCCEEDED    4', G), ('Reducer 3 .... SUCCEEDED    1', G), ('VERTICES: 03/03  100%', Y)]),
    term([('+---------+--------+', W), ('| city    | total  |', W), ('| Mumbai  | 450    |', G), ('| Pune    | 400    |', G), ('| Thane   | 150    |', G), ('3 rows selected (19.3 seconds)', Y)]),
]
see_caps = ['Kabir presses Enter on a five-line query.',
            'Hive begins by parsing. If a keyword were misspelt the error would appear now.',
            'Names are checked against the metastore. An unknown column fails here.',
            'Compilation is done. Only now does the cluster get involved.',
            '<code>EXPLAIN</code> would have shown the plan at this point: a map vertex and two reducer vertices.',
            'Tez reports each vertex finishing: 16 + 4 + 1 tasks.',
            'The sorted result arrives: Mumbai first (450), as requested by ORDER BY total DESC. Orders of Rs 100 or less were filtered out. (Time is illustrative.)']
behind_caps = ['Phase 1 · Parse: the SQL text is the input to the parser.',
               'The parser builds a tree whose branches are the clauses: FROM, SELECT, WHERE, GROUP BY, ORDER BY.',
               'Phase 2 · Analyse: the tree becomes a chain of operators, and every name is checked with the metastore. Notice that Filter comes before Group By.',
               'Phase 3 · Optimise: push the filter into the scan, read only two columns, aggregate partially on each map task.',
               'Phase 4 · Plan: cut at every ReduceSink into vertices: Map 1, Reducer 2 and Reducer 3, joined by shuffle edges.',
               'Phase 5 · Execute: Tez asks YARN for 21 containers and runs one task in each (the number of tasks per vertex depends on data size).',
               'The result is written, fetched through HiveServer2 and the temporary files are removed.']
two = anim_two('SQL to tasks', 'One query, five phases', 'Beeline output during compilation and execution', 'The query as a tree, an operator chain, a DAG and tasks', see, B1, see_caps, behind_caps)

# ---- scenario 1: MR vs Tez
def jobbox(x, y, w, label, tone):
    return label_box(x, y, w, 30, [label], tone, 8)
n1 = (t(180, 22, 'The same three-stage query', 9.6, bold=True) + jobbox(10, 40, 100, 'Map 1', 'acc') + jobbox(130, 40, 100, 'Reducer 2', 'blue') + jobbox(250, 40, 100, 'Reducer 3', 'violet') +
      arrow(112, 55, 128, 55) + arrow(232, 55, 248, 55) + cap('Three stages: scan + partial aggregate, aggregate, sort.', '', 'card', y=110, h=34))
n2 = (t(180, 22, 'MapReduce engine (old)', 9.6, 'red', bold=True) + jobbox(10, 38, 100, 'Job 1', 'acc') + jobbox(130, 38, 100, 'Job 2', 'blue') + jobbox(250, 38, 100, 'Job 3', 'violet') +
      ''.join(box(20 + k * 120, 84, 80, 22, 'red') + t(60 + k * 120, 98, 'write to HDFS', 7.8, 'red', bold=True) for k in range(3)) +
      cap('Each job writes to HDFS; the next reads it again.', 'Three job start-ups, three rounds of disk writes.', 'red', y=118, h=46))
n3 = (t(180, 22, 'Tez engine (default)', 9.6, 'green', bold=True) + box(8, 36, 344, 50, 'green') + jobbox(18, 46, 96, 'Map 1', 'acc') + jobbox(132, 46, 96, 'Reducer 2', 'blue') + jobbox(246, 46, 96, 'Reducer 3', 'violet') +
      arrow(116, 61, 130, 61, 'green') + arrow(230, 61, 244, 61, 'green') + t(180, 100, 'one DAG, data streamed between vertices', 8.6, 'green', bold=True) +
      cap('One job: no HDFS write between stages.', 'Containers are re-used between tasks.', 'green', y=118, h=46))
n4 = (t(180, 22, 'Also in Tez', 9.6, 'acc', bold=True) + ''.join(t(26, 46 + k * 18, s, 8.6, anchor='start') for k, s in enumerate(['• Vectorised execution: process 1,024 rows at a time', '• Container reuse and sessions: less start-up', '• Dynamic reducer count: adapt to real data size', '• LLAP (optional): cached data, warm code'])) +
      cap('Most of Hive’s speed-up since 2014 came from Tez + ORC.', '', 'green', y=130, h=34))
n5 = (t(180, 26, 'How to check which engine you use', 9.6, 'acc', bold=True) + tall(30, 40, 300, 54, 'Beeline', ['SET hive.execution.engine;', 'hive.execution.engine=tez'], 'card', 8.4) + t(180, 120, 'If you see “mr”, you are on a legacy setup: expect slower queries.', 8.6, 'ink2') + cap('Know your engine before you tune.', '', 'blue', y=130, h=34))
s1 = anim_one('Real-time scenario 1', 'MapReduce vs Tez: the same plan, a different engine',
              'The same three-stage plan can run on two engines. Compare how they move data between stages.',
              'Engines compared', 'A three-stage query run as three MapReduce jobs writing to HDFS, versus one Tez DAG', [n1, n2, n3, n4, n5],
              ['Our query has three stages. The plan is the same whichever engine runs it.',
               'MapReduce runs each stage as a separate job and writes the output to HDFS before the next job reads it.',
               'Tez runs the whole plan as one DAG and streams data between vertices without writing it to HDFS in between.',
               'Tez also adds vectorised execution, container re-use and run-time adjustment of reducer counts.',
               'You can check your engine with SET hive.execution.engine; modern Hive reports tez.'],
              hid='scenario-engines')

# ---- scenario 2: optimiser savings
def row(y, label, frac, col, txt):
    return t(14, y + 11, label, 8.2, anchor='start') + '<rect x="136" y="%d" width="150" height="14" rx="4" class="s-card2"/>' % y + fill(136, y, max(2, round(150 * frac)), 14, col, rx=4) + t(346, y + 11, txt, 8, 'ink', anchor='end', bold=True)
o1 = (t(180, 20, 'Naive plan: 2 TB, 10 columns', 9.6, 'red', bold=True) + row(34, 'Data read', 1, 'red', '2,000 GB') + row(58, 'Rows shuffled', 1, 'red', '12 million') + cap('Without optimisation Hive would read everything', 'and shuffle every qualifying row. (Illustrative.)', 'red', y=88, h=46))
o2 = (t(180, 20, 'Column pruning', 9.6, 'green', bold=True) + row(34, 'Data read', .2, 'green', '400 GB') + row(58, 'Rows shuffled', 1, 'red', '12 million') + cap('Only city and amount are read: 2 of 10 columns.', 'Works best with ORC or Parquet.', 'green', y=88, h=46))
o3 = (t(180, 20, '+ Predicate pushdown', 9.6, 'green', bold=True) + row(34, 'Data read', .06, 'green', '120 GB') + row(58, 'Rows shuffled', 1, 'red', '12 million') + cap('Row groups that cannot contain amount > 100 are skipped.', 'ORC / Parquet statistics make it possible.', 'green', y=88, h=46))
o4 = (t(180, 20, '+ Partial aggregation', 9.6, 'green', bold=True) + row(34, 'Data read', .06, 'green', '120 GB') + row(58, 'Rows shuffled', .02, 'green', '608 rows') + cap('Each of 16 map tasks sends at most 38 rows.', 'The shuffle becomes tiny.', 'green', y=88, h=46))
o5 = (t(180, 24, 'Check it yourself with EXPLAIN', 9.6, 'acc', bold=True) + ''.join(t(26, 48 + k * 17, s, 8.4, anchor='start', mono=True) for k, s in enumerate(['Filter Operator       -> filter is early', 'Select Operator       -> columns listed', 'Group By  mode: hash  -> partial aggregation', 'Reduce Output Operator -> shuffle boundary'])) + cap('Learn to see these four lines in any plan.', '', 'blue', y=124, h=34))
s2 = anim_one('Real-time scenario 2', 'What the optimiser saves: reading and shuffling',
              'Follow the amount of data read and shuffled as each optimisation is applied to the same query. Numbers are illustrative to show the order of magnitude.',
              'Optimiser savings', 'Bars showing data read and rows shuffled shrinking as column pruning, predicate pushdown and partial aggregation are applied', [o1, o2, o3, o4, o5],
              ['Without optimisation Hive would read every column of every row and shuffle all qualifying rows.',
               'Column pruning: only city and amount are needed, so with a columnar format 80% of the bytes are never read.',
               'Predicate pushdown: stripes or row groups whose statistics show no amount above 100 are skipped.',
               'Partial aggregation: each map task sums its own rows first, so only a few hundred rows are shuffled.',
               'In EXPLAIN look for the Filter, Select, Group By (mode hash) and Reduce Output operators to confirm all this happens.'],
              hid='scenario-optimiser')

# ---- scenario 3: join strategies
j1 = (label_box(10, 14, 130, 40, ['orders', '2 TB (big)'], 'acc', 8.8) + label_box(10, 66, 130, 40, ['cities', '200 KB (tiny)'], 'blue', 8.8) + t(250, 38, 'SELECT … FROM orders o', 8.2, mono=True) + t(250, 52, 'JOIN cities c ON o.city = c.city', 8.2, mono=True) +
      cap('A big table joins a tiny one: very common.', 'Hive must choose a join strategy.', 'card', y=124, h=46))
j2 = (label_box(6, 10, 80, 34, ['orders'], 'acc', 8.4) + label_box(6, 56, 80, 34, ['cities'], 'blue', 8.4) + ''.join(f'<path d="M88 {27 if k < 1 else 73}L150 {24 + k * 34}" style="fill:none;stroke:#E05A8A;stroke-width:1.2"/>' for k in range(3)) + ''.join(f'<path d="M88 73L150 {24 + k * 34}" style="fill:none;stroke:#E05A8A;stroke-width:1.2;opacity:.5"/>' for k in range(3)) +
      ''.join(label_box(152, 8 + k * 34, 90, 28, [f'Reducer {k+1}'], 'violet', 8) for k in range(3)) + t(300, 40, 'both tables', 8.4, 'red', bold=True) + t(300, 54, 'shuffled by key', 8.4, 'red', bold=True) +
      cap('Shuffle join: both tables are repartitioned by key.', 'The 2 TB table crosses the network.', 'red', y=124, h=46))
j3 = (label_box(6, 56, 80, 34, ['cities'], 'blue', 8.4) + ''.join(f'<path d="M88 73L{150} {20 + k * 34}" style="fill:none;stroke:#2F7D5B;stroke-width:1.6"/>' for k in range(3)) +
      ''.join(label_box(152, 8 + k * 34, 108, 28, [f'Map task {k+1}: orders block + cities'], 'green', 6.6) for k in range(3)) + t(318, 40, 'small table', 8, 'green', bold=True) + t(318, 54, 'copied to every task', 8, 'green', bold=True) +
      cap('Map (broadcast) join: copy the small table everywhere.', 'No shuffle of the big table, no reducers.', 'green', y=124, h=46))
j4 = (t(180, 22, 'How Hive decides', 9.6, 'acc', bold=True) + ''.join(t(24, 46 + k * 17, s, 8.4, anchor='start') for k, s in enumerate(['hive.auto.convert.join = true (default)', 'Statistics say one side fits in memory → map join', 'Threshold: hive.auto.convert.join.noconditionaltask.size', 'No statistics? Hive may guess wrong. Run ANALYZE TABLE.'])) + cap('Good statistics = good join choices.', '', 'blue', y=122, h=34))
j5 = (t(180, 22, 'Watch out: skew', 9.6, 'red', bold=True) + ''.join(fill(30 + k * 56, 100 - h, 40, h, 'red' if k == 1 else 'green') + t(50 + k * 56, 112, f'R{k+1}', 8, bold=True) for k, h in enumerate([20, 70, 18, 22, 19])) + t(180, 128, 'One reducer holds a hot key (a customer with millions of orders)', 8.4, 'red', bold=True) +
      cap('Skewed keys make one reducer slow while the rest wait.', 'Hive has skew-join settings; first look at the data.', 'red', y=140, h=46))
s3 = anim_one('Real-time scenario 3 · advanced', 'Shuffle join, map join and skew',
              'Joins are where plans differ most. See how Hive picks a join strategy and what can go wrong.',
              'Join strategies', 'A big table joined to a tiny table by shuffle join versus map join, and a skewed key overloading one reducer', [j1, j2, j3, j4, j5],
              ['A 2 TB orders table joins a tiny cities table. Hive must choose how.',
               'Shuffle join: both tables are repartitioned by the join key and matched in reducers. The big table crosses the network.',
               'Map (broadcast) join: the tiny table is copied to every map task, which joins locally. No reducers, no shuffle of the big table.',
               'Hive picks automatically if statistics show a table fits within the configured size. Fresh statistics matter.',
               'Skew: if one key is far more common than the others, one reducer gets most of the work and the whole stage waits for it.'],
              hid='scenario-joins')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>A query becomes a job: five phases, seven frames</h2>
  <p>Left: what Beeline prints. Right: the form the query takes inside HiveServer2, from text to tree to operators to a graph of tasks.</p>
''' + two + '''
  <p>Three live scenarios follow: MapReduce versus Tez, what the optimiser saves, and the difference between shuffle joins and map joins.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

# ---------------------------------------------------------------- real-world
uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Reading plans in daily work</h2>
''' + usecase(
    '<rect x="16" y="20" width="88" height="50" rx="6" class="s-board"/><text x="24" y="40" font-size="8" class="mono" style="fill:#9FD3B8">EXPLAIN SELECT …</text><text x="24" y="54" font-size="8" class="mono" style="fill:#F5C77E">Map 1 · Reducer 2</text>',
    '1. Check before you schedule',
    'Before putting a report in the nightly schedule, an engineer runs <code>EXPLAIN</code> and checks that the filter is early, partitions are pruned and no huge shuffle join is planned. It takes a second and saves hours.',
    ['New report', '*EXPLAIN', 'Fix or schedule']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + ''.join(fill(24 + k * 14, 58 - [30, 12, 8, 6, 5][k], 10, [30, 12, 8, 6, 5][k], 'red' if k == 0 else 'green') for k in range(5)),
    '2. The reducer that never finishes',
    'In the Tez progress table, 199 of 200 reducers finish in a minute; one runs for an hour. That is skew: one key has most rows. The team adds a salt to the key or handles the hot key separately.',
    ['Progress table', '*One slow reducer', 'Skew handling']) + '\n' + usecase(
    '<rect x="16" y="20" width="88" height="50" rx="6" class="s-card2"/>' + t(60, 40, 'ANALYZE TABLE', 8, bold=True, mono=True) + t(60, 56, 'COMPUTE STATISTICS', 7.4, 'ink2', mono=True),
    '3. Fresh statistics, better plans',
    'After a big load, the optimiser still believes a table has 10,000 rows and chooses a map join that runs out of memory. Running <code>ANALYZE TABLE … COMPUTE STATISTICS</code> after loads gives it the true sizes.',
    ['Big load', '*ANALYZE TABLE', 'Correct join type']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="44" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 40, 'Tez UI', 9, 'blue', bold=True) + t(60, 56, 'DAG · vertices · times', 7.4, 'ink2'),
    '4. Finding the slow stage',
    'The Tez UI shows each vertex’s time and tasks. If Reducer 3 takes 90% of the run time, the sort at the end is the bottleneck, and the fix is a different design, not a bigger cluster.',
    ['Slow query', '*Tez UI', 'Slowest vertex']) + '\n' + usecase(
    '<path d="M20 66h80" class="s-line"/><rect x="26" y="26" width="18" height="40" rx="3" class="s-red"/><rect x="51" y="44" width="18" height="22" rx="3" style="fill:var(--track)"/><rect x="76" y="54" width="18" height="12" rx="3" class="s-green"/>',
    '5. Cost control on the cloud',
    'Cloud bills depend on how long containers run. A plan that reads 2 TB instead of 120 GB costs real money every night. Teams review the plans of their most expensive jobs first.',
    ['Cloud bill', '*Read volume', 'Rewrite the query']) + '''
  <p class="muted">Examples are simplified. Numbers are illustrative.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> you should know the Hive components from <a href="../03-hive-architecture-and-metastore/">Lesson 1.3</a> and the idea of map, shuffle and reduce from <a href="../01-prerequisites-sql-hdfs-and-yarn-refresher/">Lesson 1.1</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
