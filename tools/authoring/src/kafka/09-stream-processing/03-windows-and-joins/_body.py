import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from kafkakit import *
C = 'l93_windows.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('An order stamped 12:00:08 arrives after one stamped 12:00:12. Which 10-second window does it count in, and what if it arrives a minute late?',
    'Streams work in <b>event time</b>. Windows group records by their timestamps; a <b>grace period</b> decides how late a record may still be counted. In our lab a record 4 s late updated its window from 3 to 4; one that arrived after the grace was <b>silently dropped</b>. We also built hopping and session windows, enriched orders with a menu table, and matched orders with payments within 5 minutes.',
    ['Tumbling, hopping, sliding and session windows.',
     'Event time, stream time, grace and suppress.',
     'Stream-table and stream-stream joins.'])
cmap = concept_map('Concept map. Beginner: timestamp, window, count per window. Intermediate: tumbling, hopping, session windows, grace, stream-table join. Advanced: stream time, suppress, stream-stream join windows, co-partitioning, foreign-key joins.',
    [[('ts', 'Record timestamp', 'event time', None), ('kt', 'KTable', 'Lesson 9.2', B + '09-stream-processing/02-ktables-and-state-stores/')],
     [('tw', 'Tumbling', 'fixed, no overlap', None), ('hw', 'Hopping', 'overlap', None), ('sw', 'Session', 'gap based', None), ('gr', 'Grace + late data', 'how late', None)],
     [('su', 'Suppress', 'final result', None), ('stj', 'Stream-table join', 'enrich', None), ('ssj', 'Stream-stream join', 'within window', None), ('sp', 'Spark watermarks', 'Lesson 9.4', B + '09-stream-processing/04-kafka-with-spark/')]],
    [('ts', 'tw'), ('tw', 'hw'), ('tw', 'sw'), ('tw', 'gr'), ('gr', 'su'), ('kt', 'stj'), ('ts', 'ssj'), ('gr', 'sp')],
    {'tw', 'hw', 'sw', 'gr', 'su', 'stj', 'ssj'},
    '<b>Builds on:</b> <a href="../02-ktables-and-state-stores/">9.2</a>. <b>Next:</b> <a href="../04-kafka-with-spark/">9.4 Spark and Flink</a>.')
whw = why_how_where(
    'Business questions are about time (“orders per minute”, “payment within 5 minutes”) and about combining streams (“order + latest price”). Networks and phones deliver events late and out of order.',
    'Each record carries a timestamp. Streams tracks <b>stream time</b> (max timestamp seen per task). A window closes when stream time passes window end + grace; later records for it are dropped. Joins keep windowed or table state so matching records can meet.',
    'Per-minute dashboards, rate limits and fraud (N events per window), user sessions, enrichment with reference data, order–payment and click–impression matching.',
    'Time only moves when new records arrive (no wall-clock closing by default). Joins need co-partitioned inputs (same key, same partition count), except GlobalKTable and foreign-key joins.')

def win(hl=-1):
    o = t(176, 20, 'event time (s) →', 7.4)
    o += ''.join(t(10 + s * 11, 112, str(s), 6.2) for s in range(0, 31, 5))
    for k, (a, b) in enumerate([(0, 10), (10, 20), (20, 30)]):
        o += box(10 + a * 11, 34, (b - a) * 11 - 4, 22, 'acc' if k == hl else 'blue', rx=3) + t(10 + a * 11 + (b - a) * 5.5, 49, f'[{a},{b})', 7, bold=True)
    for s, tn in [(1, 'green'), (4, 'green'), (9, 'green'), (12, 'green'), (8, 'amber'), (21, 'green'), (7, 'red')]:
        o += box(6 + s * 11, 68 + (12 if tn != 'green' else 0), 10, 10, tn, rx=5)
    return o
scene_svg = scene('A time line from 0 to 30 seconds with tumbling 10-second windows; dots mark events at 1, 4, 9, 12 and 21 seconds, a late event at 8 seconds within grace (amber) and a late event at 7 seconds after grace (red).', win(),
                  'Late but within grace: <tspan font-weight="700" class="s-acc">counted</tspan>. After grace: dropped.')
dialogue = '''K> Sir, the “orders per 10 seconds” chart changes after it was drawn. A window that said 3 later said 4.
A> A phone sent an order late. Streams uses the order’s own timestamp, so it put it in the right window and updated it. That is <b>event time</b>.
R> And if it arrives very late?
A> After the <b>grace period</b> the window is closed and the record is dropped. If you only want the final number, use <b>suppress</b>. Let’s test every case.'''

lv = '''
LEVELS> Windows and joins at three levels
L1> Train coaches
      <ul>
        <li>Tumbling windows are coaches of fixed length; hopping windows are overlapping coaches; a session is a group of friends who keep sitting together while they keep talking (gap). Grace is how long the door stays open after the train leaves the platform.</li>
      </ul>
L2> The DSL
      <ul>
        <li><code>TimeWindows.ofSizeAndGrace(10 s, 5 s)</code> (tumbling), <code>.advanceBy(5 s)</code> (hopping), <code>SlidingWindows</code> (by time difference), <code>SessionWindows.ofInactivityGapWithNoGrace(5 s)</code>.</li>
        <li>Windowed keys look like <code>Mumbai@[0s,10s)</code>: start inclusive, end exclusive. Results are updates; <code>suppress(untilWindowCloses(...))</code> emits one final result per window.</li>
        <li>Joins: stream–table (<code>join/leftJoin</code>, lookup latest value, table updates don’t emit), stream–stream (<code>JoinWindows</code>, both sides buffered), table–table, and foreign-key table joins.</li>
      </ul>
L3> Time internals
      <ul>
        <li>Timestamps come from the record (CreateTime) or a <code>TimestampExtractor</code> (e.g. a field). Stream time = max timestamp seen by the task; window close = end + grace.</li>
        <li>Session windows merge: a new event within the gap of two sessions joins them; old session results are deleted (null) and a merged one emitted, as our lab shows.</li>
        <li>Suppress needs the right serdes on the materialized store; otherwise a ClassCastException appears (we hit it in the lab and fixed it with <code>Materialized.with(String, Long)</code>).</li>
      </ul>
/LEVELS
'''
WT = figure('Window types: tumbling windows of 10 seconds do not overlap; hopping windows of 10 seconds advancing by 5 overlap, so an event at 7 seconds is in two windows; session windows grow while events are less than 5 seconds apart.',
    t(16, 22, 'Same events, three window types', 8.6, 'ink', anchor='start', bold=True) +
    t(16, 48, 'tumbling', 7.6, 'ink', anchor='start', bold=True) + box(100, 36, 108, 18, 'blue', rx=3) + box(212, 36, 108, 18, 'blue', rx=3) + box(324, 36, 108, 18, 'blue', rx=3) +
    t(16, 82, 'hopping', 7.6, 'ink', anchor='start', bold=True) + box(100, 64, 220, 14, 'amber', rx=3) + box(210, 80, 220, 14, 'amber', rx=3) + box(170, 64, 8, 30, 'acc', rx=3) + t(440, 66, 'event at 7 s in [0,10) and [5,15)', 7.2, anchor='start') +
    t(16, 120, 'session', 7.6, 'ink', anchor='start', bold=True) + box(100, 110, 40, 18, 'green', rx=3) + box(320, 110, 12, 18, 'green', rx=3) + t(440, 122, 'gap 5 s: 0 and 3 merge; 20 new', 7.2, anchor='start'),
    h=170, caption='Times in seconds from 12:00:00 (lab).')
extra = '''

  <h3>Window types side by side</h3>
''' + WT

types_html = table(['Window', 'Defined by', 'Overlap?', 'Example'], [
    ['Tumbling', 'size', 'no', 'orders per 10 s'], ['Hopping', 'size + advance', 'yes', '1-min average every 10 s'],
    ['Sliding', 'max time difference', 'yes (per record)', 'two logins within 30 s'], ['Session', 'inactivity gap', 'no (per key)', 'user visits'],
], minw=560) + table(['Join', 'State', 'Emits when', 'Lab'], [
    ['stream–table', 'table', 'stream record arrives', 'order × menu price'], ['stream–stream', 'both sides, windowed', 'match within window', 'order + payment ≤ 5 min'],
    ['table–table', 'both tables', 'either side updates', '—'], ['FK table–table', 'both', 'either side', '—'],
], minw=560)
warn = 'Records later than the grace period are dropped without an error (only a metric: dropped-records). Choose grace from real lateness data, and alert on the dropped-records metric.'

steps = [
    ('Step 1 · Tumbling with grace',
     code('java', 'Win93.java', 'stream.groupByKey()\n  .windowedBy(TimeWindows.ofSizeAndGrace(Duration.ofSeconds(10), Duration.ofSeconds(5)))\n  .count()', sec('== 1)', '== 2)')),
     'Each event updates its window. At t=8 (stream time 12) window [0,10) closes at 10+5=15, so it is still open: count 4. At t=7 after stream time 21, the window is closed: dropped.'),
    ('Step 2 · Only final results',
     code('java', 'Win93.java', '.count(Materialized.with(Serdes.String(), Serdes.Long()))\n.suppress(Suppressed.untilWindowCloses(Suppressed.BufferConfig.unbounded()))', sec('== 2)', '== 3)')),
     'No intermediate updates. When stream time reached 21 (≥ 15), the final [0,10) = 4 was emitted once. [10,20) will be emitted when stream time passes 25.'),
    ('Step 3 · Hopping',
     code('java', 'Win93.java', 'TimeWindows.ofSizeWithNoGrace(Duration.ofSeconds(10)).advanceBy(Duration.ofSeconds(5))', sec('== 3)', '== 4)')),
     'One event at 7 s lands in two overlapping windows.'),
    ('Step 4 · Sessions',
     code('java', 'Win93.java', 'SessionWindows.ofInactivityGapWithNoGrace(Duration.ofSeconds(5))', sec('== 4)', '== 5)')),
     'Events at 0 and 3 are within 5 s: the session [0,0] is deleted and replaced by [0,3] with count 2. Event at 20 starts a new session. The late event at 6 arrives after stream time 20: dropped.'),
    ('Step 5 · Stream-table join',
     code('java', 'Win93.java', 'KTable<String,String> menu = b.table("menu");\norders.leftJoin(menu, (qty, price) -> price == null ? "?" : qty * price)', sec('== 5)', '== 6)')),
     'Each order uses the price at that moment. leftJoin keeps pizza with a missing price. A price change alone emits nothing; the next order sees 45.'),
    ('Step 6 · Stream-stream join',
     code('java', 'Win93.java', 'orders.join(payments, (o, p) -> o + " PAID " + p, JoinWindows.ofTimeDifferenceWithNoGrace(Duration.ofMinutes(5)))', sec('== 6)')),
     'A payment 2 minutes after the order matched. One 10 minutes later did not: outside the join window.'),
]
see = [term([('[0,10) 1,2,3 → 4 (late ok)', G), ('t=7 after grace: none', RD)], size=6.8), term([('only at t=21:', W), ('Mumbai@[0s,10s) 4', G)], size=7.0),
       term([('Pune@[0s,10s) 1', G), ('Pune@[5s,15s) 1', G)], size=7.0), term([('[0,0] deleted (merged)', Y), ('[0,3] = 2', G)], size=7.0),
       term([('idli 2 x 40 = 80', G), ('pizza ? (not on menu)', Y), ('later: 2 x 45 = 90', G)], size=6.8), term([('order-1 PAID (2 min)', G), ('order-2: none (10 min)', RD)], size=7.0)]
B1 = [win(0), win(0), win(1), win(-1), win(2), win(-1)]
B1 = [b + cap(c, '', tn, y=126, h=30) for b, c, tn in zip(B1, ['Late within grace counted', 'Final result only', 'Overlapping windows', 'Sessions merge', 'Enrich with table', 'Match within 5 min'], ['green', 'blue', 'amber', 'violet', 'green', 'blue'])]
two = anim_two('Windows and joins', 'Time, lateness, matching', 'Real outputs (TopologyTestDriver)', 'On the time line', see, B1, ['Tumbling.', 'Suppress.', 'Hopping.', 'Session.', 'Enrich.', 'Match.'], ['Grace.', 'Final.', 'Overlap.', 'Merge.', 'Lookup.', 'Window.'])
pe = peel('The late record, layer by layer', 'Mumbai at t=7 s after stream time 21. (From the lab.)',
    [('Arrive', ''), ('Stream time', ''), ('Find window', ''), ('Check close', ''), ('Drop', ''), ('Metric', '')],
    [['Arrive', 'timestamp 12:00:07', '', ''], ['Stream time', 'max seen = 21 s', '', ''], ['Find window', '[0,10)', '', ''],
     ['Check close', 'end 10 + grace 5 = 15', '21 > 15 → closed', ''], ['Drop', 'not counted', 'no output', ''], ['Metric', 'dropped-records', 'increments', 'log: skipping']],
    ['In.', 'Clock.', 'Bucket.', 'Closed?', 'Drop.', 'Count.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'Rate limit', 'More than 5 orders per minute from one phone. (Typical.)', ('Tumbling count', 'Window + filter'), [
    ('Bot places orders', '20/min', 'Abuse.', 'red'), ('count per phone per 1 min', 'tumbling', 'Measure.', 'blue'),
    ('filter count > 5', 'alerts topic', 'Detect.', 'green'), ('Block service consumes alerts', 'act', 'Stop.', 'green'),
    ('Tune grace', 'mobile lateness', 'Accurate.', 'blue')], ['Abuse.', 'Count.', 'Detect.', 'Block.', 'Tune.'], 'scenario-rate') + \
       five('Real-time scenario 2', 'Join produces nothing', 'Order–payment join empty. (Typical.)', ('Co-partitioning', 'Same key, same partitions'), [
    ('orders 6 partitions', 'payments 3', 'Mismatch.', 'red'), ('Streams refuses', 'TopologyException', 'Startup fails.', 'red'),
    ('Repartition payments', 'to 6, same key', 'Fix.', 'green'), ('Keys must match', 'order id on both', 'Check.', 'amber'),
    ('Matches flow', 'within window', 'Done.', 'blue')], ['Mismatch.', 'Fail.', 'Repartition.', 'Key.', 'Flow.'], 'scenario-copart') + \
       five('Real-time scenario 3 · advanced', 'Dashboard flickers', 'Window updates on every event. (Typical.)', ('Suppress', 'Emit final results only'), [
    ('Chart redraws 1000×/min', 'every update', 'Noisy.', 'amber'), ('Downstream billing double counts', 'treats updates as new', 'Bug.', 'red'),
    ('suppress(untilWindowCloses)', 'one final row', 'Fix.', 'green'), ('Latency = size + grace', 'trade-off', 'Accept.', 'amber'),
    ('Or consumers upsert by window key', 'alternative', 'Choose.', 'blue')], ['Noise.', 'Bug.', 'Suppress.', 'Wait.', 'Upsert.'], 'scenario-suppress')
assemble(HERE, h2_story='Counting by time when events arrive late', hook_html=hk,
    narration='TiffinGo’s “orders per 10 seconds” chart keeps changing after it is drawn, and finance wants orders matched with payments that arrive minutes later.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Windows and joins',
    formal='<b>Windowing</b> groups records with the same key by their timestamps into finite buckets: tumbling (fixed, non-overlapping), hopping (fixed, overlapping), sliding (by time difference) and session (separated by inactivity gaps). A <b>grace period</b> bounds how late an out-of-order record is accepted, measured against <b>stream time</b>. <b>Joins</b> combine streams and tables by key: stream–table joins look up the current table value; stream–stream joins match records whose timestamps lie within a join window.',
    simple='Windows cut time into buckets so you can count “per 10 seconds”. Late events still land in the right bucket if they are not too late. Joins match records with the same key, like an order with its price or its payment.',
    term_rows=[('Event time', 'Time in the record.'), ('Stream time', 'Max timestamp seen.'), ('Tumbling', 'Fixed, no overlap.'), ('Hopping', 'Fixed, overlapping.'), ('Session', 'Gap-based per key.'), ('Grace', 'Allowed lateness.'), ('Suppress', 'Emit final only.'), ('Join window', 'Max time apart.')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('Windows use the server clock.', 'They use record timestamps (event time).', 'Step 1.'),
               ('Late data causes an error.', 'It is silently dropped after grace.', 'Step 1: t=7.'),
               ('A table update re-emits joins.', 'Only stream records trigger stream–table joins.', 'Step 5.')],
    exam='“Explain windows and joins in Kafka Streams.” Tumbling/hopping/sliding/session; event time vs stream time; grace and late drops; suppress for final results; stream-table (lookup), stream-stream (JoinWindows), table-table, FK joins; co-partitioning.',
    types_h2='Windows and joins', types_html=types_html, warn=warn,
    steps_h2='Six time experiments', steps_intro='All outputs are real, produced with Kafka Streams 4.4.0 TopologyTestDriver (exact, repeatable event times; same engine as a live app).',
    steps=steps, two=two, peel_intro='Now peel the dropped record.', peel_html=pe,
    scen_intro='Three live scenarios: rate limiting, an empty join, and a flickering dashboard.', scen=scen,
    uc_h2='Windows and joins at work', ucs=[uc_('min', 'per minute', 'blue', '1. Per-minute metrics', 'Orders, revenue, errors.', ['Events', '*tumbling', 'Chart']),
        uc_('sess', 'sessions', 'violet', '2. User sessions', 'Visits split by inactivity.', ['Clicks', '*session', 'Visits']),
        uc_('enr', 'enrich', 'green', '3. Enrichment', 'Orders + menu/customer tables.', ['Orders', '*join', 'Enriched']),
        uc_('match', 'match', 'amber', '4. Matching events', 'Order + payment, ad + click.', ['Two streams', '*window join', 'Matched'])],
    uc_note='Examples are simplified descriptions of common practice.',
    pre='<b>Before you start:</b> <a href="../02-ktables-and-state-stores/">9.2 KTables</a>.')
