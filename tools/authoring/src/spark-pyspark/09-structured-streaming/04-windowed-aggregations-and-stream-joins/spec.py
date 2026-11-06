import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='09-structured-streaming', lesson='04-windowed-aggregations-and-stream-joins', n='9.4',
    module_label='Module 9 · Structured Streaming',
    title='Windowed aggregations and stream joins',
    desc='Windows and joins in Structured Streaming with PySpark 4.3.0: the same five clicks in tumbling (3/1/1), sliding (3/4/2/1) and session windows (4 sessions), a stream-static join with inner and left joins, a stream-stream join of orders and deliveries within 30 minutes with watermarks where the left outer join emits undelivered orders after the watermark, and state growing 4 → 7 → 9 without watermarks.',
    og_desc='Tumbling, sliding and session windows on the same clicks, and a stream-stream join that finds orders not delivered in 30 minutes.',
    minutes=30, level='Intermediate → Advanced',
    lead='Streams are grouped by time and joined with tables or other streams. This lesson computes <b>tumbling, sliding and session windows</b> on the same events, runs a <b>stream-static join</b>, and joins orders with deliveries as a <b>stream-stream join</b> with watermarks, including an outer join that reports late deliveries. <b>All outputs are real</b> (PySpark 4.3.0).',
    chips=['PySpark 4.3.0', '3 window types', 'Stream-stream outer join', 'Runs in your browser (Python)'],
)

MAIN = '''# Assigning events to windows (minutes after 10:00)
clicks = [0, 2, 3, 9, 12]

def tumbling(m, size=5):
    s = m // size * size
    return [(s, s + size)]

def sliding(m, size=10, slide=5):
    first = (m // slide) * slide - size + slide
    return [(s, s + size) for s in range(first, m + 1, slide) if s <= m < s + size]

from collections import Counter
print("tumbling:", sorted(Counter(w for m in clicks for w in tumbling(m)).items()))
print("sliding :", sorted(Counter(w for m in clicks for w in sliding(m)).items()))
'''
RUN = dict(
    heading='Run the code: assigning windows',
    intro='<p>How each click is assigned to windows. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('    s = m // size * size', 'Tumbling: exactly one window per event.'),
        ('    return [(s, s + size) for s in range(first, m + 1, slide) if s <= m < s + size]', 'Sliding: an event belongs to size ÷ slide windows (here 2).'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. -5 is 09:55. Then try slide = 2.', code=None),
        dict(label='2 · Predict first: sessions', hint='<b>Predict first:</b> u1 clicks at 0, 2, 9 with a 5-minute gap.',
             code='''clicks, gap = [0, 2, 9], 5
sessions, start, last = [], clicks[0], clicks[0]
for c in clicks[1:]:
    if c - last > gap:
        sessions.append((start, last + gap)); start = c
    last = c
sessions.append((start, last + gap))
print(sessions)
'''),
        dict(label='3 · Range condition', hint='Does a delivery match within 30 minutes?',
             code='''for order, deliver in [(0, 25), (5, 50), (20, 30)]:
    print(order, deliver, order <= deliver <= order + 30)
'''),
        dict(label='4 · Outer emission', hint='When can an unmatched order be emitted with null?',
             code='''order, limit, watermark = 5, 30, 87   # minutes after 10:00
print("emit null" if watermark > order + limit else "keep waiting")
'''),
        dict(label='5 · Spot the error', hint='A stream-stream outer join without watermarks.', expect='error',
             code='''left_wm, right_wm, range_cond = None, None, False
assert left_wm and right_wm and range_cond, "outer stream-stream joins need watermarks on both sides and a time-range condition"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: windows and joins',
    intro='<p>In the <code>pyspark</code> shell with the lab files. <b>Outputs are real</b> (PySpark 4.3.0).</p>',
    items=[
        dict(title='1 · Session windows', cmd='c.groupBy("user", F.session_window("ts", "5 minutes")).count()', file='pyspark',
             output="[('u1', '10:00', '10:07', 2), ('u1', '10:09', '10:14', 1), ('u2', '10:03', '10:08', 1), ('u2', '10:12', '10:17', 1)]", note='Collected from the memory sink.'),
        dict(title='2 · Left outer stream-stream', cmd='os_.join(ds, cond, "leftOuter")', file='pyspark',
             output="[leftOuter] batch 3: [(2, None), (3, None)]", note='After the watermark.'),
        dict(title='3 · No watermark', cmd='[p["stateOperators"][0]["numRowsTotal"] for p in q.recentProgress]', file='pyspark',
             output='[4, 7, 9]', note='Grows forever.'),
    ],
)

TRACE = dict(
    heading='A stream-stream join, batch by batch',
    intro='<p>Orders wait in state until a delivery arrives.</p>',
    code='''state = {}
batches = [([(1, 0), (2, 5)], [(1, 25)]), ([(4, 20)], [(4, 30)])]
for orders, deliveries in batches:
    for oid, t in orders:
        state[oid] = t
    for oid, d in deliveries:
        if oid in state and state[oid] <= d <= state[oid] + 30:
            print("match", oid)
            del state[oid]
print("waiting:", state)
''',
    notes={5: 'Buffer :: Orders kept in state.', 7: 'Range :: Within 30 minutes.', 10: 'Waiting :: Order 2 still in state.'},
)

WORKED_INTRO = 'Three time-based problems at TiffinGo.'
EXAMPLES = [
    dict(level='b', tag='Windows · choose', title='Which window?',
         problem='<p>Three requests: orders per hour; orders in the last hour every 10 min; app visits.</p>',
         inp='three questions',
         approach=['Fixed buckets → tumbling.', 'Rolling → sliding.', 'Activity → session.'],
         code='''print({"per hour": "tumbling", "last hour every 10 min": "sliding", "visits": "session"})
''', notes={1: 'Match :: The question picks the window.'},
         tryit='Steps 1–2.'),
    dict(level='i', tag='Joins · static', title='Enrich orders',
         problem='<p>Add restaurant names to an order stream.</p>',
         inp='dimension table',
         approach=['Stream-static join.', 'Left join to keep unknown restaurants.', 'Refresh the dimension if it changes.'],
         code='''code = 'orders_stream.join(restaurants, "rest_id", "left")'
print(code)
''', notes={1: 'Stateless :: No watermark needed.'},
         tryit='Step 3.'),
    dict(level='a', tag='Joins · stream', title='Size the join state',
         problem='<p>2,000 orders/min, 30-min range, 10-min watermark.</p>',
         inp='rates',
         approach=['Rows kept ≈ rate × (range + delay).', 'Both sides.', 'Check memory.'],
         code='''rate, keep_min = 2000, 30 + 10
print(rate * keep_min, "order rows in state (plus deliveries)")
''', notes={1: 'Bound :: Only possible with watermarks.'},
         tryit='Step 4.'),
]

QUIZ = mix([
    dict(q='Beginner: Non-overlapping fixed windows are…', options=['Sliding', 'Tumbling', 'Session', 'Global'], answer=1,
         why='One window per event.'),
    dict(q='Beginner: Function for session windows?', options=['window', 'session_window', 'gap_window', 'over'], answer=1,
         why='With a gap duration.'),
    dict(q='Beginner: Does a stream-static join need state?', options=['Yes', 'No', 'Only outer', 'Only inner'], answer=1,
         why='Joined per batch.'),
    dict(q='Intermediate: Sliding 10 min / 5 min: each event is in…', options=['1 window', '2 windows', '5 windows', '10 windows'], answer=1,
         why='3+4+2+1 = 10 for 5 clicks.'),
    dict(q='Intermediate: Which stream-static join is NOT supported (stream on left)?', options=['inner', 'left outer', 'right outer', 'none'], answer=2,
         why='Would need the whole stream.'),
    dict(q='Intermediate: Order 2 delivered after 45 minutes with a 30-min range…', options=['Matches', 'Does not match', 'Error', 'Duplicates'], answer=1,
         why='Outside the range.'),
    dict(q='Advanced: When does a left outer stream-stream join emit nulls?', options=['Immediately', 'After the watermark passes the range', 'Never', 'At query stop'], answer=1,
         why='Batch 3 in the lab.'),
    dict(q='Advanced: Join state without watermarks…', options=['Is bounded', 'Grows forever (4→7→9)', 'Is cleared each batch', 'Errors'], answer=1,
         why='Slow memory leak.'),
])

REVISION = [
    'Tumbling: one window per event (3/1/1); sliding: overlapping (3/4/2/1).',
    'Session windows close after an inactivity gap (4 sessions).',
    'Stream-static join: stateless; inner and left (stream left).',
    'Stream-stream join: both sides buffered in state.',
    'Watermarks on both sides + time-range condition bound the state.',
    'Outer join nulls appear only after the watermark (orders 2, 3).',
    'Without watermarks state grows: 4 → 7 → 9 rows.',
]
FAQ = [
    ('Can I aggregate after a stream-stream join?', 'Yes in recent Spark versions with append mode and watermarks, with some restrictions; check the docs for your version.'),
    ('How do I refresh the static side?', 'Read it inside foreachBatch, or rely on file/table sources being re-read each batch; cached DataFrames do not refresh.'),
    ('What is a global window?', 'Grouping without a window (e.g. groupBy(user)) keeps a running total per key forever.'),
    ('Can session gaps be dynamic?', 'Yes, session_window accepts an expression for the gap, per row.'),
    ('Are window boundaries aligned to the epoch?', 'Yes, tumbling windows start at multiples of the size from 1970-01-01 UTC, unless you give a startTime offset.'),
]

PRACTICE_INTRO = 'Programs about windows and stream joins.'
PROBLEMS = [
    dict(level='easy', title='Tumbling bucket', stmt='Window of 10:12 with 5-min windows.', inp='12',
         code='''print(12 // 5 * 5)
''', explain='10:10.'),
    dict(level='easy', title='Sliding count', stmt='Windows per event: size 15, slide 5.', inp='15, 5',
         code='''print(15 // 5)
''', explain='3.'),
    dict(level='easy', title='In range?', stmt='Delivery at 10:50 for order 10:05, 30-min limit.', inp='5, 50',
         code='''print(5 <= 50 <= 35)
''', explain='No match.'),
    dict(level='medium', title='Sessions', stmt='Count sessions with a 5-min gap.', inp='[0, 2, 9, 30]',
         code='''c, gap, n = [0, 2, 9, 30], 5, 1
for a, b in zip(c, c[1:]):
    n += (b - a) > gap
print(n)
''', explain='3 sessions.'),
    dict(level='medium', title='Matches', stmt='Orders matched within 30 min.', inp='orders, deliveries',
         code='''o = {1: 0, 2: 5, 4: 20}
d = {1: 25, 2: 50, 4: 30}
print([k for k in o if o[k] <= d[k] <= o[k] + 30])
''', explain='[1, 4].'),
    dict(level='medium', title='Unmatched', stmt='Orders without timely delivery.', inp='same data + order 3',
         code='''o = {1: 0, 2: 5, 3: 10, 4: 20}
d = {1: 25, 2: 50, 4: 30}
print([k for k in o if not (k in d and o[k] <= d[k] <= o[k] + 30)])
''', explain='[2, 3], as in the lab.'),
    dict(level='business', title='State size', stmt='Rows in state at 2,000 orders/min, 40 min kept.', inp='2000, 40',
         code='''print(2000 * 40)
''', explain='80,000 rows.'),
    dict(level='business', title='Refund cost', stmt='Coupons for 2% late orders of 50,000 a day at ₹50.', inp='2%, 50000, 50',
         code='''print("₹", int(50000 * 0.02 * 50))
''', explain='₹50,000/day: worth monitoring live.'),
]

SCN_INTRO = 'Window types and stream joins are common senior streaming questions.'
SCENARIOS = (
    scn('Any company · Spark', 'Fresher', '“Tumbling vs sliding vs session”',
        'Explain the three windows.',
        'examples?',
        '<p>Tumbling: fixed non-overlapping buckets (orders per 5 minutes). Sliding: fixed length moving by a slide, overlapping (last 10 minutes every 5). Session: grows with activity and closes after a gap (a user visit).</p>', 'Mixing up slide and size.') +
    scn('Data engineering', 'Mid-level', 'Enrichment',
        'Join an event stream with a product table.',
        'how?',
        '''<ul>
          <li>Stream-static join; no state or watermark.</li>
          <li>Left join to keep unknown keys.</li>
          <li>Refresh the table via foreachBatch or a table source.</li>
        </ul>''', 'Treating the product table as a stream.') +
    scn('Data engineering', 'Mid-level', 'Undelivered orders',
        'Find orders without a delivery within 30 minutes, live.',
        'design?',
        '''<ol>
          <li>Watermarks on both streams.</li>
          <li>Left outer join with a 30-minute range condition.</li>
          <li>Null deliveries are emitted after the watermark; alert on them.</li>
        </ol>''', 'Inner join only (never shows missing deliveries).') +
    scn('Platform', 'Senior', 'Join memory',
        'A stream-stream join job keeps growing in memory.',
        'diagnose?',
        '''<ul>
          <li>Check state rows over time (numRowsTotal).</li>
          <li>Missing watermarks or range condition → unbounded state.</li>
          <li>Add them (new checkpoint), use RocksDB state store.</li>
        </ul>''', 'Only adding executors.')
)
