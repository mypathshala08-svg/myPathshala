import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from svgkit import scn
BODY = body(HERE)
META = dict(module='09-stream-processing', lesson='03-windows-and-joins', n='9.3', module_label='Module 9 · Stream processing',
    title='Windows and joins',
    desc='Time in Kafka Streams: event time and stream time, tumbling, hopping, sliding and session windows, grace periods and late records, suppress for final results, and stream–table and stream–stream joins. Real Kafka Streams 4.4 outputs (TopologyTestDriver): a late record counted within grace, one dropped after grace, sessions merging, orders enriched with live menu prices, and payments matched within 5 minutes.',
    og_desc='Late by 4 s: counted. Late after grace: dropped. Kafka Streams windows and joins with real outputs.',
    minutes=26, level='Advanced',
    lead='How do you count “per 10 seconds” when events arrive late? We run <b>tumbling, hopping and session windows</b>, test <b>grace</b> and <b>suppress</b>, and do two kinds of <b>joins</b>. <b>All outputs are real.</b>',
    chips=['Grace: 3 → 4', 'Dropped after grace', 'Sessions merge', 'Runs in your browser (Python)'])
MAIN = '''# Tumbling window 10 s with grace 5 s, driven by event time
SIZE, GRACE = 10, 5
counts, stream_time = {}, 0
for t, note in [(1, ""), (4, ""), (9, ""), (12, ""), (8, "late"), (21, ""), (7, "late")]:
    stream_time = max(stream_time, t)
    start = t // SIZE * SIZE
    if stream_time >= start + SIZE + GRACE:
        print(f"t={t:2} {note:4} window [{start},{start+SIZE}) closed -> dropped")
        continue
    counts[start] = counts.get(start, 0) + 1
    print(f"t={t:2} {note:4} window [{start},{start+SIZE}) = {counts[start]}")
'''
RUN = dict(heading='Run the code: windows and grace', intro='<p>The lab’s first experiment in Python. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('    stream_time = max(stream_time, t)', 'Stream time only moves forward.'), ('    if stream_time >= start + SIZE + GRACE:', 'Closed = end + grace passed.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>. Set GRACE = 0.', code=None),
        dict(label='2 · Predict first: hopping', hint='<b>Predict first:</b> windows (size 10, advance 5) containing t=7.', code='print([(s, s + 10) for s in range(0, 10, 5) if s <= 7 < s + 10])\n'),
        dict(label='3 · Session', hint='Gap 5 s, events 0, 3, 20.', code='ev, gap, sess = [0, 3, 20], 5, []\nfor e in ev:\n    if sess and e - sess[-1][1] <= gap: sess[-1][1] = e\n    else: sess.append([e, e])\nprint(sess)\n'),
        dict(label='4 · Join window', hint='Payment 600 s after order, window 300 s.', code='print(abs(600 - 0) <= 300)\n'),
        dict(label='5 · Spot the error', hint='Suppress without serdes.', expect='error', code='raise TypeError("ClassCastException: Windowed cannot be cast to String (set Materialized.with(String, Long))")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC: test windows', intro='<p>Needs kafka-streams-test-utils (in Kafka libs). No broker needed. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Compile', cmd='javac -proc:none -cp "libs/*" -d out src/Win93.java', file='terminal', output='', note='TopologyTestDriver.'),
           dict(title='2 · Run', cmd='java -cp "out:libs/*" Win93', file='terminal', output='  event Mumbai t=8s (late, within grace) -> [KeyValue(Mumbai@[0s,10s), 4)]\n  event Mumbai t=7s (late, after grace) -> no output', note='Deterministic.')])
TRACE = dict(heading='The late record step by step', intro='<p>Clock, bucket, check.</p>',
    code='stream_time = 21\nt = 7\nstart = t // 10 * 10\nclosed = stream_time >= start + 10 + 5\nprint(start, closed)\n',
    notes={3: 'Window :: [0,10).', 4: 'Closed :: 21 ≥ 15 → dropped.'})
WORKED_INTRO = 'Three time decisions.'
EXAMPLES = [
    dict(level='b', tag='Windows · choose', title='Pick a window', problem='<p>Orders per minute chart.</p>', inp='need',
         approach=['Fixed buckets.', 'No overlap.', 'Tumbling 1 min.'], code='print("TimeWindows.ofSizeAndGrace(1 min, 30 s)")\n', notes={1: 'Tumbling :: Simple.'}, tryit='Step 1.'),
    dict(level='i', tag='Windows · grace', title='Choose grace', problem='<p>99% of mobile events arrive within 20 s.</p>', inp='lateness',
         approach=['Grace ≈ p99 lateness.', '20–30 s.', 'Monitor dropped-records.'], code='print({"grace": "30 s"})\n', notes={1: 'Data-driven :: Not a guess.'}, tryit='Warning box.'),
    dict(level='a', tag='Joins · design', title='Enrich orders', problem='<p>Add price and restaurant name.</p>', inp='design',
         approach=['Menu: KTable keyed by item (co-partitioned).', 'Restaurants: GlobalKTable (small).', 'leftJoin to keep unknown items.'], code='print("orders.leftJoin(menu).join(restaurantsGlobal, keyMapper)")\n', notes={1: 'Lookup :: Latest values.'}, tryit='Step 5.')]
QUIZ = mix([
    dict(q='Beginner: Windows group records by…', options=['Arrival on server', 'Record timestamp (event time)', 'Offset', 'Key length'], answer=1, why='Event time.'),
    dict(q='Beginner: Tumbling windows…', options=['Overlap', 'Do not overlap', 'Depend on gaps', 'Have no size'], answer=1, why='Fixed buckets.'),
    dict(q='Beginner: A record later than grace is…', options=['Counted', 'Dropped', 'Errors', 'Sent to DLQ automatically'], answer=1, why='Silently.'),
    dict(q='Intermediate: The t=8 late record changed [0,10) to…', options=['3', '4', '0', '8'], answer=1, why='Within grace.'),
    dict(q='Intermediate: suppress(untilWindowCloses) emits…', options=['Every update', 'One final result per window', 'Nothing', 'Only late data'], answer=1, why='Final only.'),
    dict(q='Intermediate: An event at 7 s in hopping (10, advance 5) belongs to…', options=['1 window', '2 windows', '3 windows', 'none'], answer=1, why='[0,10) and [5,15).'),
    dict(q='Advanced: A menu price update alone in a stream–table join…', options=['Re-emits old orders', 'Emits nothing', 'Deletes orders', 'Errors'], answer=1, why='Stream side triggers.'),
    dict(q='Advanced: Stream–stream joins require…', options=['A JoinWindows', 'A GlobalKTable', 'Compaction', 'Suppress'], answer=0, why='Time bound.')])
REVISION = ['Event time; stream time = max seen; close = end + grace.', 'Tumbling, hopping, sliding, session windows.',
    'Lab: t=8 counted (4), t=7 dropped; suppress → final 4 at t=21; hopping 2 windows; session merge [0,3]=2.', 'Stream–table join: latest price (40 → 45), leftJoin keeps pizza.', 'Stream–stream join within 5 min; co-partitioning required.']
FAQ = [('Can windows close by wall-clock time?', 'Not by default; stream time advances only with new records. Use punctuators (Processor API) or emit-on-close strategies carefully.'),
    ('What timestamp is used?', 'The record timestamp (producer CreateTime) unless you set a TimestampExtractor.'),
    ('How do I see dropped late records?', 'Metric dropped-records-total per task, plus a WARN log line.'),
    ('Are windows stored?', 'Yes, in windowed/session state stores with changelogs and retention ≥ size + grace.')]
PRACTICE_INTRO = 'Window programs.'
PROBLEMS = [
    dict(level='easy', title='Bucket', stmt='Window start for t=37, size 10.', inp='int', code='print(37 // 10 * 10)\n', explain='30.'),
    dict(level='easy', title='Close', stmt='Close time of [30,40) grace 5.', inp='ints', code='print(40 + 5)\n', explain='45.'),
    dict(level='easy', title='Late?', stmt='Stream time 50, t=38.', inp='ints', code='print(50 >= 45)\n', explain='Dropped.'),
    dict(level='medium', title='Hopping', stmt='Windows for t=12 (10, adv 5).', inp='int', code='print([(s, s + 10) for s in range(0, 20, 5) if s <= 12 < s + 10])\n', explain='[5,15),[10,20).'),
    dict(level='medium', title='Sessions', stmt='Gap 5: 0,2,10,12.', inp='list', code='ev, s = [0, 2, 10, 12], []\nfor e in ev:\n    if s and e - s[-1][1] <= 5: s[-1][1] = e\n    else: s.append([e, e])\nprint(s)\n', explain='2 sessions.'),
    dict(level='medium', title='Join', stmt='Price lookup.', inp='dict', code='menu = {"idli": 45}\nprint(2 * menu.get("idli", 0))\n', explain='90.'),
    dict(level='business', title='Rate limit', stmt='Flag > 5 per minute.', inp='dict', code='c = {"phone-1": 20, "phone-2": 3}\nprint([k for k, v in c.items() if v > 5])\n', explain='phone-1.'),
    dict(level='business', title='Unpaid', stmt='Orders without payment in 5 min.', inp='sets', code='print({"o1", "o2"} - {"o1"})\n', explain='o2.')]
SCN_INTRO = 'Windowing interview questions.'
SCENARIOS = (scn('Any company · data', 'Fresher', '“Event time vs processing time?”', 'Explain.', 'answer?', '<p>Event time is when the event happened (in the record); processing time is when the app sees it. Windows in Kafka Streams use event time, with a grace period for late events.</p>', '“Same thing.”') +
    scn('Analytics', 'Mid-level', 'Numbers too low', 'Mobile counts missing.', 'cause?', '<ul><li>Late events after grace dropped.</li><li>Increase grace, check metric.</li></ul>', 'Restart app.') +
    scn('Platform', 'Mid-level', 'Join empty', 'No matches.', 'check?', '<ul><li>Keys equal? Partitions equal?</li><li>Window wide enough?</li></ul>', 'Add partitions randomly.') +
    scn('Fintech', 'Senior', 'Final totals', 'Billing needs one number per hour.', 'design?', '<ul><li>Tumbling 1 h + grace + suppress.</li><li>Or upsert by window key.</li></ul>', 'Use every update.'))
