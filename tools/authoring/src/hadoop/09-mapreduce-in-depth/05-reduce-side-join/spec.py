import os
HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(HERE)
BODY = body(HERE)
rd = lambda f: open(os.path.join(UP, f)).read()

META = dict(
    module='09-mapreduce-in-depth', lesson='05-reduce-side-join', n='9.5',
    module_label='Module 9 · MapReduce in depth',
    title='Reduce-side join',
    desc='The reduce-side (repartition) join in Hadoop MapReduce, run on a real Hadoop 3.5.0 cluster: 5 lakh canteen orders joined with a menu file through MultipleInputs, tagged values and the item as join key. Real counters show 24.4 MB shuffled, the menu row arriving first in only 3 of 7 groups (so the reducer must buffer), 459,636 orders joined and 40,364 dropped by the inner join. Inner, left, right, full outer and anti joins, skew, memory and when to use it. Python simulation, quiz and interview scenarios.',
    og_desc='Join 5 lakh orders with a menu in MapReduce, and catch the menu row arriving last in 4 of 7 groups.',
    minutes=26, level='Intermediate',
    lead='MapReduce has no JOIN keyword, but it has something just as good: the shuffle. Map both data sets to the same key, tag where each record came from, and the reducer receives every matching record together. This lesson joins 5 lakh real orders with the menu and reads the counters that show why the reducer must be careful.',
    chips=['Real join on 5 lakh orders', 'Menu-row order measured', 'Runs in your browser (Python)'],
)

RUN = dict(
    heading='Simulate a reduce-side join',
    intro='<p>Two small inputs, tagged map output, a shuffle that mixes the order of values (as Hadoop does), and a reducer that joins. Change <code>JOIN</code> to <code>"left"</code> to keep orders without a menu row.</p>',
    code='''import random
random.seed(4)
orders = ["1,S1413,dosa,45", "2,S0973,samosa,18", "3,S0007,coffee,20", "4,S0001,dosa,45", "5,S0002,chai,15"]
menu = ["chai,drink", "samosa,snack", "dosa,meal", "thali,meal"]
JOIN = "inner"

pairs = [(o.split(",")[2], "O|" + o) for o in orders]          # OrderMapper
pairs += [(m.split(",")[0], "M|" + m.split(",")[1]) for m in menu]  # MenuMapper

groups = {}
for k, v in pairs:                                             # shuffle: group by item
    groups.setdefault(k, []).append(v)
for k in groups:
    random.shuffle(groups[k])                                  # values arrive in no fixed order

for item in sorted(groups):                                    # reducer
    category, buffered = None, []
    for v in groups[item]:
        if v.startswith("M|"):
            category = v[2:]
        else:
            buffered.append(v[2:])
    for o in buffered:
        if category is not None:
            print(o + "," + category)
        elif JOIN == "left":
            print(o + ",")                                     # no menu row: empty category
''',
    anno=[
        ('pairs = [(o.split(",")[2], "O|" + o) for o in orders]          # OrderMapper', 'The join key (item) becomes the map output key; the tag O| says “this came from orders”.'),
        ('    random.shuffle(groups[k])                                  # values arrive in no fixed order', 'Hadoop merges values from several map tasks; in our lab the menu row was first in only 3 of 7 groups.'),
        ('            buffered.append(v[2:])', 'Orders wait in a list until the category is known. This list is the memory risk of reduce-side joins.'),
    ],
    tasks=[
        dict(label='1 · Inner join', hint='Press <b>Run</b>. Which order disappeared, and which menu item never appears?', code=None),
        dict(label='2 · Left outer join', hint='<b>Predict first:</b> set <code>JOIN = "left"</code>. How many rows now?',
             code='''groups = {"coffee": ["O|3,S0007,coffee,20"], "dosa": ["O|1,S1413,dosa,45", "M|meal"], "thali": ["M|meal"]}
for item in sorted(groups):
    cat = next((v[2:] for v in groups[item] if v.startswith("M|")), None)
    for v in groups[item]:
        if v.startswith("O|"):
            print(v[2:] + "," + (cat if cat else ""))
'''),
        dict(label='3 · Anti join', hint='Print only the orders that have NO menu row (the data-quality report).',
             code='''groups = {"coffee": ["O|3,S0007,coffee,20", "O|9,S0011,coffee,20"], "dosa": ["O|1,S1413,dosa,45", "M|meal"]}
for item, vals in sorted(groups.items()):
    if not any(v.startswith("M|") for v in vals):
        for v in vals:
            print("orphan:", v[2:])
'''),
        dict(label='4 · Count the shuffle', hint='Our job shuffled 500,007 records to join 7 menu rows. What fraction of the shuffled records were menu rows?',
             code='''orders, menu_rows = 500_000, 7
print(f"menu rows are {menu_rows / (orders + menu_rows) * 100:.4f}% of the shuffle")
'''),
        dict(label='5 · Spot the error', hint='This reducer assumes the menu row comes first and writes orders immediately. Here the menu row arrives second. Fix it by buffering.',
             code='''values = ["O|1,S1413,dosa,45", "M|meal", "O|4,S0001,dosa,45"]
category = None
for v in values:
    if v.startswith("M|"):
        category = v[2:]
    else:
        print(v[2:] + "," + category)
''', expect='error'),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run it on your PC: join orders with the menu',
    intro='<p>Use the Module 8 lab cluster (Lesson 8.1). Create the data with <code>make_student_orders.py</code> (it writes <code>student_orders.csv</code> and <code>menu.csv</code>), copy the files and <code>JoinReduceSide.java</code> into <code>/tmp/mr9</code> in the namenode container, compile into <code>mr9.jar</code> and run <code>join_lab.sh</code>. The script also runs the map-side join of Lesson 9.6 for comparison.</p>',
    items=[
        dict(title='Reduce-side join', file='JoinReduceSide.java',
             cmd=rd('java/JoinReduceSide.java') + '\n// In the mr-lab folder:\n//   python3 make_student_orders.py\n//   docker exec lab8-namenode-1 mkdir -p /tmp/mr9\n//   docker cp JoinReduceSide.java lab8-namenode-1:/tmp/mr9/\n//   docker cp student_orders.csv lab8-namenode-1:/tmp/mr9/\n//   docker cp menu.csv lab8-namenode-1:/tmp/mr9/\n// Inside the container, in /tmp/mr9:\n//   hdfs dfs -D dfs.blocksize=8388608 -put -f student_orders.csv /user/hadoop/data/\n//   mkdir -p classes && javac -cp $(hadoop classpath) -d classes *.java && jar cf mr9.jar -C classes .',
             output='(compiles to mr9.jar; run it with join_lab.sh below)',
             note='The 8 MB block size gives 3 splits for the orders, so you can see values from several map tasks being merged.'),
        dict(title='Join lab: reduce-side vs map-side', file='join_lab.sh',
             cmd=rd('join_lab.sh') + '\n# Inside the namenode container:  bash /tmp/mr9/join_lab.sh',
             output=rd('tx95.txt').strip(),
             note='Real output. MENU_FIRST/MENU_NOT_FIRST will differ between runs because the merge order depends on which map task finishes first; the joined rows never do. The JoinMapSide part is explained in Lesson 9.6.'),
    ],
)

TRACE = dict(
    heading='The reducer for one item',
    intro='<p>The values for <code>dosa</code> arrive with the menu row in the middle. Watch the list grow until the category is known.</p>',
    code='''values = ["O|1,dosa,45", "M|meal", "O|4,dosa,45"]
category = None
buffered = []
for v in values:
    if v.startswith("M|"):
        category = v[2:]
    else:
        buffered.append(v[2:])
for o in buffered:
    print(o + "," + category)
''',
    notes={6: 'Menu :: The category is learned in the middle of the loop.',
           8: 'Buffer :: Orders are kept, not written, until the loop ends.',
           10: 'Join :: Only now can every order be completed.'},
)

WORKED_INTRO = 'Three reduce-side join problems: the shuffle cost, the memory risk, and choosing the join type.'
EXAMPLES = [
    dict(level='b', tag='Design · tags', title='Join students with their hostel',
         problem='<p><code>orders.csv</code>: <code>order_id,student_id,item,amount</code>. <code>students.csv</code>: <code>student_id,name,hostel</code>. The warden wants revenue per hostel. What is the join key, what do the two mappers emit, and what does the reducer write?</p>',
         inp='3 orders · 2 students',
         approach=['Join key = student_id, in both files.',
                   'Order mapper: (student_id, "O|amount"); student mapper: (student_id, "S|hostel").',
                   'Reducer: find the hostel, write (hostel, amount) for each order; a second job (or step) sums per hostel.'],
         code='''orders = ["1,S1,dosa,45", "2,S2,chai,15", "3,S1,thali,80"]
students = ["S1,Riya,Ganga", "S2,Kabir,Yamuna"]
groups = {}
for o in orders:
    f = o.split(","); groups.setdefault(f[1], []).append("O|" + f[3])
for s in students:
    f = s.split(","); groups.setdefault(f[0], []).append("S|" + f[2])
for sid, vals in sorted(groups.items()):
    hostel = next(v[2:] for v in vals if v.startswith("S|"))
    print(sid, hostel, [int(v[2:]) for v in vals if v.startswith("O|")])
''', notes={5: 'Tag :: O| and S| tell the reducer which file each value came from.'},
         tryit='Summing per hostel needs a different key (hostel), so it is a second MapReduce job, or a Hive query.'),
    dict(level='i', tag='Sizing · shuffle', title='What does a reduce-side join cost?',
         problem='<p>Join 200 GB of orders with a 50 MB menu using a reduce-side join on a 20-node cluster where each node can receive shuffle data at 100 MB/s. Roughly how long does the shuffle alone take, and how much of it is the menu?</p>',
         inp='200 GB + 50 MB · 20 × 100 MB/s',
         approach=['Everything is shuffled: both inputs.',
                   'Total bandwidth = nodes × per-node rate.',
                   'Compare with the menu size.'],
         code='''total_mb = 200 * 1024 + 50
seconds = total_mb / (20 * 100)
print(f"shuffle ≈ {seconds / 60:.1f} min; menu is {50 / total_mb * 100:.3f}% of it")
''', notes={2: 'Bandwidth :: Every reducer receives data in parallel.'},
         tryit='With a map-side join (Lesson 9.6), the shuffle disappears: the 50 MB menu is copied once to each node instead.'),
    dict(level='a', tag='Memory · skew', title='Will the reducer run out of memory?',
         problem='<p>A reducer buffers all orders of one item as Java Strings of about 40 characters (≈ 120 bytes each in memory). chai has 149,669 orders in our data; a real chain has 4 crore chai orders a month. The reduce container has a 300 MB heap. Does each case fit?</p>',
         inp='149,669 vs 4 crore · 120 B · 300 MB heap',
         approach=['Memory = records × bytes per record.',
                   'Compare with the heap.',
                   'Decide: buffer the small side instead, or stream with secondary sort.'],
         code='''for name, n in [("our lab", 149_669), ("real chain", 40_000_000)]:
    mb = n * 120 / 1024**2
    print(f"{name:10}: {mb:7.0f} MB -> {'fits' if mb < 300 else 'OutOfMemoryError'}")
''', notes={3: 'Memory :: 4 crore × 120 B is about 4.5 GB.'},
         tryit='Buffer the menu side (one row per item) and stream the orders: possible only if the menu row is guaranteed first, which secondary sort (Lesson 9.7) provides.'),
]

QUIZ = mix([
    dict(q='In a reduce-side join, what is the map output key?', options=['The file name', 'The join key, from both inputs', 'The byte offset', 'A random number'], answer=1,
         why='Same key from both sides, so the shuffle brings matches together.'),
    dict(q='Why are values tagged (O| and M|)?', options=['To compress them', 'So the reducer knows which input each value came from', 'Hadoop requires a prefix', 'To sort them'], answer=1,
         why='Both inputs produce values of the same type; the tag is the only way to tell them apart.'),
    dict(q='What lets one job use a different Mapper for each input path?', options=['setMapperClass twice', 'MultipleInputs.addInputPath', 'CombineFileInputFormat', 'The distributed cache'], answer=1,
         why='Each path gets its own InputFormat and Mapper.'),
    dict(q='In our run, MENU_NOT_FIRST=4. What does that show?', options=['4 menu rows were lost', 'The menu row can arrive after orders, so orders must be buffered', 'The job failed 4 times', '4 reducers were used'], answer=1,
         why='Values from several map tasks are merged in no guaranteed order.'),
    dict(q='Why were 40,364 orders not in the output?', options=['A bug in the mapper', 'They were coffee orders, and coffee had no menu row: an inner join drops them', 'They were duplicates', 'The reducer ran out of memory'], answer=1,
         why='ORDERS_WITHOUT_MENU=40,364, exactly the coffee orders.'),
    dict(q='Which join type keeps every order, with an empty category if no menu row exists?', options=['Inner join', 'Left outer join (orders on the left)', 'Right outer join (orders on the left)', 'Anti join'], answer=1,
         why='Left outer keeps all left-side records.'),
    dict(q='What is the main cost of a reduce-side join?', options=['It needs sorted input', 'All records of all inputs are shuffled across the network', 'It only works for small files', 'It needs a combiner'], answer=1,
         why='24.4 MB were shuffled just to meet 7 menu rows.'),
    dict(q='When is a reduce-side join the right choice?', options=['When one side fits easily in memory', 'When both data sets are large', 'When there is no join key', 'When the job is map-only'], answer=1,
         why='If one side is small, a map-side join (Lesson 9.6) avoids the shuffle.'),
])

REVISION = [
    'Reduce-side join: both mappers emit <b>(join key, tagged record)</b>; the shuffle groups by key; the reducer separates by tag and combines.',
    '<code>MultipleInputs.addInputPath(job, path, InputFormat, Mapper)</code> for each input.',
    'Values arrive in no fixed order: lab counters MENU_FIRST=3, MENU_NOT_FIRST=4. Buffer one side, or use secondary sort to put the small side first.',
    'Lab: 500,007 records and 24.4 MB shuffled, 8 groups, 459,636 joined, 40,364 coffee orders dropped, 24.8 s.',
    'Join types: inner, left outer, right outer, full outer, anti; only the reducer\'s output rule changes.',
    'Costs: everything is shuffled; buffering a hot key (chai 149,669 orders) can exhaust memory.',
    'Use when both sides are big; if one side is small, use a map-side join.',
]
FAQ = [
    ('What is a reduce-side join in Hadoop?', 'A join performed in the reduce phase. Each input has a mapper that emits the join key as the map output key and the record, tagged with its source, as the value. The shuffle sends all records with the same key to one reduce call, where the reducer separates them by tag and emits the joined records. It handles inputs of any size but shuffles all data.'),
    ('What is the difference between a map-side join and a reduce-side join?', 'A reduce-side join shuffles both data sets by the join key and joins in the reducer; it works for any sizes. A map-side join loads the small data set into every mapper\'s memory (via the distributed cache) and joins while reading the large one, with no shuffle; it needs one side small enough to fit in memory. In our lab both produced the same 459,636 rows; the map-side join took 18.9 s instead of 24.8 s.'),
    ('Why do reduce-side joins need buffering?', 'The values for a key come from several map tasks and are merged in no guaranteed order, so the reducer may see many records from one side before the matching record from the other side. It must keep them in memory until the loop is complete, unless secondary sort is used to make one side arrive first.'),
    ('How do you do an outer join in MapReduce?', 'The map side is unchanged. In the reducer, after separating the values by tag, emit unmatched records too: for a left outer join, emit every left-side record with empty fields if the right side is missing; for a right outer join, the reverse; for a full outer join, both.'),
    ('How do you handle skew in a reduce-side join?', 'A key with very many records sends them all to one reducer, which becomes slow or runs out of memory. Options: filter out junk keys like NULL, buffer only the smaller side and stream the larger with secondary sort, split (salt) the hot key across several reducers while replicating the small side, or use a map-side join when one side is small.'),
]

PRACTICE_INTRO = 'Reduce-side join exercises using the real numbers from the lab.'
PROBLEMS = [
    dict(level='easy', title='Check the counters', stmt='ORDERS_JOINED=459,636 and ORDERS_WITHOUT_MENU=40,364. Do they add up to all orders?', inp='two counters',
         code='''print(459636 + 40364 == 500000)
''', explain='True: every order was either joined or counted as unmatched; none was lost silently.'),
    dict(level='easy', title='Where do 500,007 records come from?', stmt='Map input records were 500,007. Explain the 7.', inp='orders + menu',
         code='''print(500000 + 7)
''', explain='5 lakh orders plus the 7 rows of menu_nocoffee.csv; both inputs go through map and shuffle.'),
    dict(level='easy', title='Bytes per shuffled record', stmt='24,448,645 shuffle bytes for 500,007 records. What is the average size of one tagged record?', inp='bytes / records',
         code='''print(round(24448645 / 500007, 1), "bytes")
''', explain='About 49 bytes: the whole order line plus the “O|” tag and the item key, plus framing.'),
    dict(level='medium', title='Full outer join', stmt='Write the reducer output for a full outer join: orders without a menu row get an empty category, menu items without orders get one line “,,item,category”.', inp='3 groups',
         code='''groups = {"coffee": ["O|3,coffee"], "dosa": ["O|1,dosa", "M|meal"], "thali": ["M|meal"]}
for item, vals in sorted(groups.items()):
    cat = next((v[2:] for v in vals if v.startswith("M|")), None)
    ords = [v[2:] for v in vals if v.startswith("O|")]
    for o in ords:
        print(o + "," + (cat or ""))
    if not ords:
        print(",," + item + "," + cat)
''', explain='coffee kept with a blank, dosa joined, thali printed once with no order.'),
    dict(level='medium', title='Menu first with a composite key', stmt='Sort the values by a tag rank so the menu row (rank 0) always comes before orders (rank 1), then stream without a list.', inp='mixed values',
         code='''values = ["O|1,dosa,45", "M|meal", "O|4,dosa,45"]
values.sort(key=lambda v: 0 if v.startswith("M|") else 1)
category = None
for v in values:
    if v.startswith("M|"):
        category = v[2:]
    else:
        print(v[2:] + "," + category)
''', explain='In Hadoop the sort happens in the shuffle via a composite key (item, tag) with grouping on item only: Lesson 9.7.'),
    dict(level='medium', title='Reducer load', stmt='With one reducer per item, which reducer has the most work? Use the real order counts.', inp='orders per item',
         code='''counts = {"chai": 149669, "coffee": 40364, "samosa": 69884, "vada pav": 69754, "poha": 45336, "idli": 44774, "dosa": 49927, "thali": 30292}
top = max(counts, key=counts.get)
print(top, counts[top], f"= {counts[top] / sum(counts.values()) * 100:.0f}% of all orders")
''', explain='chai: 30% of all records go to one reduce call. That is join skew.'),
    dict(level='business', title='Unmatched means lost money', stmt='The finance report used an inner join and missed every coffee order (40,364 orders at ₹20). How much revenue was missing from the report?', inp='40,364 × ₹20',
         code='''print(f"Rs {40364 * 20:,}")
''', explain='₹8,07,280 missing for one month. Count unmatched records, or use a left outer join, in every financial join.'),
    dict(level='advanced', title='Salting a hot key', stmt='Split chai into 3 reducers by appending a salt to the key on the order side, and replicate the menu row to all 3 salts. Show that every chai order still gets its category.', inp='5 chai orders',
         code='''orders = [f"O|{i},chai,15" for i in range(1, 6)]
groups = {}
for n, o in enumerate(orders):
    groups.setdefault(f"chai#{n % 3}", []).append(o)            # salt orders
for s in range(3):
    groups.setdefault(f"chai#{s}", []).append("M|drink")       # replicate menu row
for key in sorted(groups):
    cat = next(v[2:] for v in groups[key] if v.startswith("M|"))
    print(key, [v[2:] + "," + cat for v in groups[key] if v.startswith("O|")])
''', explain='Three smaller groups instead of one; the small side is copied to every salt. Spark\'s skew-join handling does the same.'),
]

SCN_INTRO = 'Joins are among the most asked MapReduce and Spark interview topics: how they work, what they cost and what goes wrong.'
SCENARIOS = '''    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Concepts · joins</span><span class="scn__tag scn__tag--level">Fresher</span></div>
      <h4>“How do you join two datasets in MapReduce?”</h4>
      <p class="scn__situation">Asked right after word count.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> key choice, tagging and the shuffle.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Reduce-side: both mappers emit (join key, tagged record) via MultipleInputs; the shuffle groups by key; the reducer separates by tag and combines.</li>
          <li>Map-side: if one side is small, load it in every mapper from the distributed cache and join while reading; no shuffle.</li>
          <li>Mention the trade-off: reduce-side works for any sizes but shuffles everything.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Debugging · data</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>The joined output has fewer rows than the orders table</h4>
      <p class="scn__situation">Finance says revenue in the joined report is lower than in the raw orders.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> inner join semantics and counters.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>An inner join drops records without a match: check a counter for unmatched keys (our lab: 40,364 coffee orders, no menu row).</li>
          <li>Fix the master data, or switch to a left outer join so unmatched rows appear with blanks.</li>
          <li>Add a reconciliation check: joined + unmatched = input.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Internals · ordering</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>“My join reducer works in testing but loses rows in production”</h4>
      <p class="scn__situation">The reducer writes orders as soon as it has the category, and assumes the dimension row comes first.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> value order is not guaranteed.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Values for a key are merged from many map tasks in no fixed order; with one map task in testing it looked ordered.</li>
          <li>Buffer one side until the loop ends, or make the order deterministic with secondary sort: composite key (join key, tag), partition and group on the join key.</li>
          <li>Add a counter for “dimension not first” to detect it.</li>
        </ul>
      </div></details>
    </article>
    <article class="scn">
      <div class="scn__head"><span class="scn__tag">Performance · skew</span><span class="scn__tag scn__tag--level">Experienced</span></div>
      <h4>One reducer of a join runs for hours; the other 199 finish in minutes</h4>
      <p class="scn__situation">Joining page views with users; one user_id is the anonymous value “0”.</p>
      <p class="scn__look"><b>The interviewer is checking:</b> skew diagnosis and fixes.</p>
      <details><summary>Show a strong answer</summary><div class="scn__answer">
        <ul>
          <li>Check reduce input records per task: one key holds most records.</li>
          <li>Filter or handle the junk key separately; salt hot keys and replicate the small side; or use a map-side join if the users table fits in memory.</li>
          <li>In Spark, adaptive query execution can split skewed partitions automatically.</li>
        </ul>
      </div></details>
    </article>
'''
