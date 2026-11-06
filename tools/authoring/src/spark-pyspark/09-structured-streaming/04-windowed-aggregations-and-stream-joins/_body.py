import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
C = 'l94_windows.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)

CLICKS = [0, 2, 3, 9, 12]
def axis(x, y, w, t0=-5, t1=20):
    sx = lambda m: x + (m - t0) / (t1 - t0) * w
    o = fill(x, y - 0.6, w, 1.2, '#8A94A0', rx=0)
    for m in range(t0, t1 + 1, 5):
        o += fill(sx(m) - 0.6, y - 3, 1.2, 6, '#8A94A0', rx=0) + t(sx(m), y + 13, ('09:55' if m < 0 else f'10:{m:02d}'), 6.2, 'ink2')
    for m in CLICKS:
        o += box(sx(m) - 4, y - 12, 8, 8, 'blue', rx=4)
    return o, sx

def wins(x, y, w, spans, tone='green', h=12, gap=16):
    o, sx = axis(x, y, w)
    for k, (a, b, n) in enumerate(spans):
        yy = y + 22 + k * gap
        o += box(sx(a), yy, sx(b) - sx(a) - 2, h, tone, rx=3) + t(sx(a) + (sx(b) - sx(a)) / 2, yy + 9, str(n), 7, 'ink', bold=True)
    return o

# ---------------------------------------------------------------- story
sc_ = (t(20, 22, 'clicks at 10:00, 10:02, 10:03, 10:09, 10:12', 7.4, 'ink2', anchor='start', bold=True) +
       wins(20, 48, 350, [(0, 5, 3), (5, 10, 1), (10, 15, 1)], 'green', h=11, gap=14) +
       box(400, 12, 232, 132, 'card') + t(516, 30, 'Measured', 8.6, bold=True) +
       ''.join(t(412, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ('tumbling 5m: 3 | 1 | 1', 'green'), ('sliding 10m/5m: 3 4 2 1', 'blue'),
           ('session gap 5m: 4 sessions', 'violet'), ('stream-static: 103 → null', 'amber'),
           ('stream-stream: 2 late → null', 'green'), ('no watermark: state 4→7→9', 'red')])))
scene_svg = scene('Windows group events by time, and joins combine a stream with a table or with another stream. We counted the same five clicks with tumbling, sliding and session windows, joined an order stream with a restaurant table, and joined orders with deliveries within 30 minutes.', sc_,
                  'Joining two streams means <tspan font-weight="700" class="s-acc">remembering one side</tspan> until the other arrives.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Which orders were not delivered in 30 minutes?”</h2>
  <div class="story">
    <p class="narration">TiffinGo promises delivery in 30 minutes. Orders and delivery confirmations arrive on two different Kafka topics. Operations wants a live list of late orders, plus app usage per user session and orders per 5 minutes.</p>

{scene_svg}

K> Sir, joining two tables is easy. Why is joining two streams special?
A> When an order arrives, its delivery has not happened yet. Spark must keep the order in <b>state</b> until a matching delivery comes, or until it is sure none will. Without limits, it would remember every order forever.
R> And the windows?
A> Tumbling, sliding and session windows answer different questions. Today we compute all three on the same clicks, then do a stream-static join and a stream-stream join with watermarks, including an outer join that reports the undelivered orders. All outputs are real (PySpark 4.3.0).
  </div>
</section>
'''

lv = '''
LEVELS> Windows and joins at three levels
L1> A restaurant’s day
      <ul>
        <li>Tumbling: “orders per hour”, each hour its own box. Sliding: “orders in the last hour, checked every 15 minutes”. Session: “one visit = until the guest leaves for more than 30 minutes”.</li>
        <li>Stream-stream join: the waiter keeps each order slip on the counter until the dish is served, and throws away slips older than the kitchen’s promise.</li>
      </ul>
L2> The API
      <ul>
        <li><code>F.window(ts, "5 minutes")</code>, <code>F.window(ts, "10 minutes", "5 minutes")</code>, <code>F.session_window(ts, "5 minutes")</code>.</li>
        <li>Stream-static: <code>stream.join(static_df, key, how)</code>.</li>
        <li>Stream-stream: watermarks on both sides + a time-range condition, e.g. <code>deliver_ts BETWEEN order_ts AND order_ts + INTERVAL 30 MINUTES</code>.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>5 clicks: tumbling 3/1/1, sliding 3/4/2/1 (each click in 2 windows), 4 sessions for 2 users.</li>
        <li>Stream-static left join kept order 103 with a null restaurant.</li>
        <li>Stream-stream left outer join emitted orders 2 and 3 with null delivery once the watermark passed; without watermarks state grew 4 → 7 → 9.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Windowed aggregations and stream joins</h2>
''' + def_block(
    'A <b>windowed aggregation</b> groups a stream by event-time buckets. <b>Tumbling</b> windows are fixed, non-overlapping intervals (<code>window(ts, "5 minutes")</code>); <b>sliding</b> windows have a length and a slide, so each event belongs to several windows (<code>window(ts, "10 minutes", "5 minutes")</code>); <b>session</b> windows (<code>session_window(ts, gap)</code>) grow while events keep arriving within the gap and close after a period of inactivity. A <b>stream-static join</b> joins each micro-batch with a static DataFrame and is stateless; inner and left outer (stream on the left) are supported. A <b>stream-stream join</b> buffers rows of both streams in state so future rows can match past ones; to bound that state and to emit outer-join results, both inputs need watermarks and the join condition needs an event-time range constraint.',
    'Windows put events into time buckets: fixed boxes (tumbling), overlapping boxes (sliding) or activity-based boxes (sessions). Joining a stream with a fixed table is simple. Joining two streams means keeping rows from both sides until matches arrive; watermarks and a time limit in the join tell Spark when it can forget them.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Tumbling window', 'Fixed, non-overlapping.'),
    ('Sliding window', 'Length + slide, overlapping.'),
    ('Session window', 'Closes after an inactivity gap.'),
    ('Stream-static join', 'Stream × fixed table, no state.'),
    ('Stream-stream join', 'Both sides buffered in state.'),
    ('Time-range condition', 'Limits how far apart matches can be.'),
    ('Outer join emission', 'Nulls emitted after the watermark.'),
    ('Join state', 'Buffered rows of both sides.'),
]) + '''

  <h3>Three windows, same five clicks</h3>
''' + table(['Window', 'Code', 'Result (lab)'], [
    ['Tumbling 5 min', '<code>window("ts", "5 minutes")</code>', '10:00–05: 3, 10:05–10: 1, 10:10–15: 1'],
    ['Sliding 10 min / 5 min', '<code>window("ts", "10 minutes", "5 minutes")</code>', '09:55: 3, 10:00: 4, 10:05: 2, 10:10: 1'],
    ['Session, gap 5 min', '<code>session_window("ts", "5 minutes")</code>', 'u1: 10:00–10:07 (2), 10:09–10:14 (1); u2: two of 1'],
], minw=640) + lv + '''
EXAM> “How do stream-stream joins work in Spark?” Both streams are buffered in a state store so rows can match rows that arrive later. For inner joins, watermarks plus an event-time range condition let Spark drop old state; for outer joins they are required, because unmatched rows are emitted with nulls only when the watermark guarantees no match can still arrive. Stream-static joins need no state; the static side is re-read per batch unless cached.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Supported join types</h2>
''' + table(['Left', 'Right', 'Inner', 'Left outer', 'Right outer', 'Full outer'], [
    ['Static', 'Static', 'Yes', 'Yes', 'Yes', 'Yes'],
    ['Stream', 'Static', 'Yes', 'Yes', 'No', 'No'],
    ['Static', 'Stream', 'Yes', 'No', 'Yes', 'No'],
    ['Stream', 'Stream', 'Yes (watermarks advised)', 'Watermark + range needed', 'Watermark + range needed', 'Watermark + range needed'],
], minw=640) + '''
WARN> A stream-stream join without watermarks <b>works</b>, and that is the trap: results look right in testing while state grows with every row (4 → 7 → 9 rows in our tiny lab, millions in production) until batches slow down and executors run out of memory. Always add <code>withWatermark</code> on both inputs and a time bound in the join condition. Outer results also arrive late by design: an unmatched order appears only after the watermark has passed its 30-minute limit.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Windows, then joins</h2>
  <p>All outputs are real: PySpark 4.3.0, <code>local[2]</code>, UTC. Inputs are JSON files read as streams; for the stream-stream join each file is one micro-batch (<code>maxFilesPerTrigger=1</code>) so the order of arrival is controlled.</p>
''' + stepper([
    ('Step 1 · Tumbling and sliding windows',
     code('python', 'l94_windows_joins.py', 'c = spark.readStream.schema("ts timestamp, user string").json(clicks)\nc.groupBy(F.window("ts", "5 minutes")).count()                 # tumbling\nc.groupBy(F.window("ts", "10 minutes", "5 minutes")).count()   # sliding', sec('== 1)', '== 3)')),
     'Tumbling: each click lands in exactly one 5-minute box: 3, 1, 1. Sliding windows of 10 minutes every 5 minutes overlap, so each click is counted <b>twice</b> (3 + 4 + 2 + 1 = 10 = 5 × 2). Note the 09:55 window: sliding windows start before the first event. Sliding is for “last 10 minutes, updated every 5”.'),
    ('Step 2 · Session windows',
     code('python', 'l94_windows_joins.py', 'c.groupBy("user", F.session_window("ts", "5 minutes")).count()', sec('== 3)', '== 4)')),
     'u1 clicked at 10:00 and 10:02, so the session runs from 10:00 to 10:07 (last event + 5-minute gap). The 10:09 click came after the gap closed, so it opened a <b>new</b> session. Session windows have no fixed length; they follow user activity.'),
    ('Step 3 · Stream-static join',
     code('python', 'l94_windows_joins.py', 'rest = spark.createDataFrame([(1, "Biryani House", "Mumbai"), (2, "Dosa Point", "Pune")], …)\no.join(rest, "rest_id")            # inner\no.join(rest, "rest_id", "left")    # left outer, stream on the left', sec('== 4)', '== 5)')),
     'Each micro-batch of orders is joined with the restaurant table like a normal batch join: no state, no watermark. Order 103 has an unknown restaurant: dropped by the inner join, kept with <code>None</code> by the left join. If the static table changes, re-read it per batch (it is not cached unless you cache it).'),
    ('Step 4 · Stream-stream join with watermarks',
     code('python', 'l94_windows_joins.py', 'os_ = orders_stream.withWatermark("order_ts", "10 minutes")\nds  = deliveries_stream.withWatermark("deliver_ts", "10 minutes")\ncond = F.expr("d_order_id = order_id AND deliver_ts BETWEEN order_ts AND order_ts + INTERVAL 30 MINUTES")\nos_.join(ds, cond, "inner")  /  os_.join(ds, cond, "leftOuter")', sec('== 5)', '== 6)')),
     'Order 1 matched its 10:25 delivery as soon as it arrived. Order 2 was delivered at 10:50, more than 30 minutes after 10:05, so it does <b>not</b> match. Orders 2 and 3 found no delivery and stayed in <b>state</b>, waiting, while later orders 4 and 5 matched in their batches. The left outer join emitted orders <b>2 and 3 with null</b> in batch 3, only after the watermark (from 11:40 events) proved no delivery could still qualify. State ended at 2 rows.'),
    ('Step 5 · Without watermarks',
     code('python', 'l94_windows_joins.py', 'orders.join(deliveries, F.expr("d_order_id = order_id"))   # no watermark, no time bound', sec('== 6)')),
     'Same data, no watermarks: the join still produces matches, but state rows only grow, <b>4 → 7 → 9</b>, because Spark can never be sure an old order will not get a delivery. In production this is a slow memory leak.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('tumbling: 3 | 1 | 1', G), ('sliding : 3 | 4 | 2 | 1', Y)], size=7.6),
    term([('u1 10:00-10:07: 2', G), ('u1 10:09-10:14: 1', G), ('u2 10:03-10:08, 10:12-10:17', W)], size=7.4),
    term([('inner: 101, 102', G), ('left : 101, 102, (103, None)', Y)], size=7.6),
    term([('leftOuter b3: (2, None), (3, None)', G), ('state rows at end: 2', G), ('no watermark: 4 -> 7 -> 9', RD)], size=7.2),
]
B1 = [
    t(180, 14, 'Tumbling vs sliding', 9.4, bold=True) + wins(20, 40, 320, [(0, 5, 3), (-5, 5, 3), (0, 10, 4)], 'green', h=10, gap=13) + cap('Sliding windows overlap.', '', 'blue', y=144, h=30),
    t(180, 14, 'Sessions follow activity', 9.4, bold=True) + wins(20, 40, 320, [(0, 7, 2), (9, 14, 1)], 'violet', h=12, gap=16) + t(300, 80, 'u1', 8, 'violet', bold=True) + cap('Gap of 5 min closes a session.', '', 'green', y=144, h=30),
    t(180, 14, 'Stream-static: no state', 9.4, bold=True) + opbox(20, 50, 'micro-batch', 'orders', 'blue', 110, 32) + t(150, 70, '⋈', 12, 'ink2') + opbox(170, 50, 'restaurants', 'static table', 'green', 110, 32) + t(310, 70, 'per batch', 7.4, 'ink2') + cap('Like a batch join, every batch.', '', 'green', y=144, h=30),
    t(180, 14, 'Stream-stream: buffer both', 9.4, bold=True) + opbox(20, 40, 'orders state', 'until +30 min', 'blue', 130, 32) + opbox(210, 40, 'deliveries state', 'until watermark', 'violet', 130, 32) + t(180, 100, 'watermark passes → emit nulls, drop state', 7.2, 'ink2') + cap('Watermarks bound the state.', '', 'green', y=144, h=30),
]
see_caps = ['Tumbling and sliding.', 'Session windows.', 'Stream-static join.', 'Stream-stream join.']
behind_caps = ['Window assignment.', 'Gap-based sessions.', 'Stateless join per batch.', 'Join state and watermarks.']
two = anim_two('Windows and stream joins', 'Time buckets and remembered rows', 'Real lab outputs', 'What Spark does', see, B1, see_caps, behind_caps)

e1 = (t(180, 22, 'Orders + deliveries topics', 9.4, bold=True) + t(180, 56, 'promise: 30 minutes', 8.4, 'ink2') + cap('Two streams.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Watermark both, 10 min', 9.4, bold=True) + t(180, 56, 'delivered within 30 min of order', 8.4, 'ink2') + cap('Range condition.', '', 'green', y=150, h=34))
e3 = (t(180, 22, 'leftOuter join', 9.4, bold=True) + t(180, 56, 'orders with no delivery → null', 8.4, 'ink2') + cap('Late orders appear.', '', 'green', y=150, h=34))
e4 = (t(180, 22, 'Emitted after the watermark', 9.4, bold=True) + t(180, 56, 'orders 2, 3 in batch 3 (lab)', 8.4, 'ink2') + cap('Not instantly.', '', 'amber', y=150, h=34))
e5 = (t(180, 22, 'Alert ops + refund coupon', 9.4, 'acc', bold=True) + t(180, 56, 'from the null rows', 8.4, 'ink2') + cap('SLA monitoring.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'The 30-minute promise',
              'Outer stream-stream joins for SLA breaches. (Typical; behaviour from our lab.)',
              'SLA join', 'A left outer stream-stream join with watermarks reports orders without a timely delivery', [e1, e2, e3, e4, e5],
              ['Two topics.', 'Watermarks.', 'Outer join.', 'After wm.', 'Alert.'],
              hid='scenario-sla')
b1 = (t(180, 22, 'App usage per session', 9.4, bold=True) + t(180, 56, 'product wants session length', 8.4, 'ink2') + cap('No fixed window fits.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'session_window 30 min', 9.4, bold=True) + t(180, 56, 'per user_id', 8.4, 'ink2') + cap('Activity-based.', '', 'green', y=150, h=34))
b3 = (t(180, 22, 'Add a watermark', 9.4, bold=True) + t(180, 56, 'so sessions can close', 8.4, 'ink2') + cap('Append mode works.', '', 'green', y=150, h=34))
b4 = (t(180, 22, 'Sessions written once', 9.4, bold=True) + t(180, 56, 'start, end, clicks', 8.4, 'ink2') + cap('Final rows.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Gap = product decision', 9.4, 'acc', bold=True) + t(180, 56, '5 min in lab, 30 min typical', 8.4, 'ink2') + cap('Changes the counts.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'What is a session?',
              'Session windows. (Typical; behaviour from our lab.)',
              'Sessions', 'Session windows group a user’s events until an inactivity gap', [b1, b2, b3, b4, b5],
              ['Question.', 'session_window.', 'Watermark.', 'Output.', 'Gap.'],
              hid='scenario-session')
u1 = (t(180, 22, 'Click × impression join', 9.4, bold=True) + t(180, 56, 'no watermark, “it works”', 8.4, 'ink2') + cap('Tests pass.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'Week 2: batches 10x slower', 9.4, bold=True) + t(180, 56, 'state: 300 million rows', 8.4, 'ink2') + cap('4 → 7 → 9 in our lab.', '', 'red', y=150, h=34))
u3 = (t(180, 22, 'Add watermarks + range', 9.4, bold=True) + t(180, 56, 'click within 1 h of impression', 8.4, 'ink2') + cap('State bounded.', '', 'green', y=150, h=34))
u4 = (t(180, 22, 'New checkpoint needed', 9.4, bold=True) + t(180, 56, 'state schema changes', 8.4, 'ink2') + cap('Plan a backfill.', '', 'amber', y=150, h=34))
u5 = (t(180, 22, 'Review checklist', 9.4, 'acc', bold=True) + t(180, 56, 'every stream join: wm + range', 8.4, 'ink2') + cap('Prevent it.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'The join that leaked memory',
              'Unbounded join state. (Typical; state growth from our lab.)',
              'Join state', 'Stream-stream joins without watermarks and range conditions keep growing state', [u1, u2, u3, u4, u5],
              ['Works.', 'Slower.', 'Bound it.', 'Checkpoint.', 'Checklist.'],
              hid='scenario-leak')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Time buckets and remembered rows</h2>
  <p>Left: real outputs. Right: how windows and joins work.</p>
''' + two + '''
  <p>Three live scenarios follow: a delivery SLA, user sessions, and a join that leaked memory.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Windows and joins at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'SLA', 12, 'blue', bold=True) + t(60, 58, 'breaches', 7.4, 'ink2'),
    '1. Delivery SLAs',
    'Orders joined with deliveries within 30 minutes; unmatched orders become alerts.',
    ['Orders ⋈ deliveries', '*left outer', 'Late list']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'ads', 12, 'green', bold=True) + t(60, 58, 'attribution', 7.4, 'ink2'),
    '2. Ad attribution',
    'Clicks joined with impressions within an hour to compute click-through rates.',
    ['Impressions ⋈ clicks', '*1 h range', 'CTR']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'session', 10, 'violet', bold=True) + t(60, 58, 'analytics', 7.4, 'ink2'),
    '3. Session analytics',
    'Session windows measure visit length and pages per visit.',
    ['Clicks', '*session_window', 'Sessions']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'trend', 12, 'acc', bold=True) + t(60, 58, 'sliding', 7.4, 'ink2'),
    '4. Moving averages',
    'Sliding windows give “orders in the last 15 minutes, every minute” for surge pricing.',
    ['Orders', '*sliding window', 'Surge signal']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'enrich', 11, 'acc', bold=True) + t(60, 58, 'static', 7.4, 'ink2'),
    '5. Enrichment',
    'Events are joined with dimension tables (restaurants, zones) as stream-static joins.',
    ['Event stream', '*⋈ dimension', 'Enriched']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> watermarks in <a href="../03-output-modes-event-time-and-watermarks/">9.3</a>, joins in <a href="../../06-transformations/02-joins/">6.2</a>, batch windows in <a href="../../06-transformations/03-window-functions/">6.3</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
