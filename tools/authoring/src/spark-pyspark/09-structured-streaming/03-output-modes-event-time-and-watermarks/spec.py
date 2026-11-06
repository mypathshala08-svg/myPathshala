import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
from sparkkit import tables
BODY = body(HERE)

META = dict(
    module='09-structured-streaming', lesson='03-output-modes-event-time-and-watermarks', n='9.3',
    module_label='Module 9 · Structured Streaming',
    title='Output modes, event time and watermarks',
    desc='Event-time windows and watermarks with PySpark 4.3.0, batch by batch: five deterministic micro-batches with late orders into 5-minute windows, complete vs update vs append output modes, the error for append without a watermark, a 5-minute watermark finalising each window once (watermark 10:06, 10:11, 10:17), a very late order dropped (numRowsDroppedByWatermark = 1) instead of changing 1419 to 9196, and state bounded to 2 rows.',
    og_desc='Batch-by-batch proof of how Spark watermarks finalise windows, drop very late data and bound state, in complete, update and append modes.',
    minutes=32, level='Intermediate → Advanced',
    lead='Events arrive late and out of order. This lesson aggregates orders into 5-minute <b>event-time windows</b> over five controlled micro-batches and shows exactly what <b>complete</b>, <b>update</b> and <b>append</b> modes write, and how a <b>watermark</b> finalises windows, drops very late data and bounds state. <b>All outputs are real</b> (PySpark 4.3.0).',
    chips=['PySpark 4.3.0', 'Batch-by-batch output', 'Watermark values shown', 'Runs in your browser (Python)'],
)

MAIN = '''# A watermark, batch by batch (5-minute windows, 5-minute delay)
batches = [[1, 2, 4], [6, 3, 11], [16, 2, 12], [22], [3, 24]]   # event minutes after 10:00
delay = 5
max_seen, wm, state, emitted = 0, None, {}, []

for b, events in enumerate(batches):
    for m in events:
        w = m // 5 * 5
        if wm is not None and w + 5 <= wm and w not in state:
            print(f"batch {b}: 10:{m:02d} dropped (window 10:{w:02d} already final)")
            continue
        state[w] = state.get(w, 0) + 1
    final = sorted(w for w in state if wm is not None and w + 5 <= wm)
    for w in final:
        emitted.append(w); del state[w]
    print(f"batch {b}: watermark {wm}, emitted {final}, state {sorted(state)}")
    max_seen = max(max_seen, max(events))
    wm = max_seen - delay
'''
RUN = dict(
    heading='Run the code: a watermark in miniature',
    intro='<p>A simplified model of the lab’s append run. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('    wm = max_seen - delay', 'The watermark for the next batch: maximum event time seen so far minus the allowed delay.'),
        ('    final = sorted(w for w in state if wm is not None and w + 5 <= wm)', 'A window is final once the watermark has passed its end; append mode writes it now, exactly once.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then set <code>delay = 10</code>: when is 10:00 emitted?', code=None),
        dict(label='2 · Predict first: watermark', hint='<b>Predict first:</b> max event 10:11, delay 5 minutes.',
             code='''max_event, delay = 11, 5
print(f"watermark 10:{max_event - delay:02d}")
'''),
        dict(label='3 · Which window?', hint='Window start for an event at 10:13 with 5-minute windows.',
             code='''m = 13
print(f"10:{m // 5 * 5:02d} - 10:{m // 5 * 5 + 5:02d}")
'''),
        dict(label='4 · Mode output', hint='What each mode writes when one of 5 windows changed.',
             code='''windows, changed = 5, 1
print({"complete": windows, "update": changed, "append": "only final windows"})
'''),
        dict(label='5 · Spot the error', hint='append mode on an aggregation without a watermark.', expect='error',
             code='''mode, has_watermark = "append", False
assert has_watermark or mode != "append", "STREAMING_OUTPUT_MODE.UNSUPPORTED_OPERATION: append needs a watermark for aggregations"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: watermarks',
    intro='<p>In the <code>pyspark</code> shell with the lab files. <b>Outputs are real</b> (PySpark 4.3.0).</p>',
    items=[
        dict(title='1 · Append without watermark', cmd='plain.writeStream.outputMode("append").format("console").start()', file='pyspark',
             output='[STREAMING_OUTPUT_MODE.UNSUPPORTED_OPERATION] Invalid streaming output mode: append. This output mode is not supported for streaming aggregations without watermark …', note='Refused at start.'),
        dict(title='2 · Watermark in progress', cmd='q.lastProgress["eventTime"]["watermark"]', file='pyspark',
             output="'2026-11-05T10:17:00.000Z'", note='max event − 5 min.'),
        dict(title='3 · Dropped rows', cmd='q.lastProgress["stateOperators"][0]["numRowsDroppedByWatermark"]', file='pyspark',
             output='1', note='The 7777 order.'),
    ],
)

TRACE = dict(
    heading='Computing the watermark',
    intro='<p>Follow the watermark across three batches.</p>',
    code='''delay = 5
max_seen = 0
for batch in [[1, 2, 4], [6, 3, 11], [16, 2, 12]]:
    max_seen = max(max_seen, max(batch))
    wm = max_seen - delay
    print(wm)
''',
    notes={4: 'Max :: Late events never lower it.', 5: 'Watermark :: Used for the next batch.'},
)

WORKED_INTRO = 'Three event-time decisions at TiffinGo.'
EXAMPLES = [
    dict(level='b', tag='Event time · windows', title='Revenue per 5 minutes',
         problem='<p>Group orders into 5-minute windows by order time.</p>',
         inp='event_time column',
         approach=['window("event_time", "5 minutes").', 'groupBy the window.', 'Sum amount.'],
         code='''code = 'ev.groupBy(F.window("event_time", "5 minutes")).agg(F.sum("amount"))'
print(code)
''', notes={1: 'Event time :: Not processing time.'},
         tryit='Step 1.'),
    dict(level='i', tag='Watermark · delay', title='Choose the delay',
         problem='<p>99% of orders arrive within 8 minutes, 99.9% within 20.</p>',
         inp='lateness distribution',
         approach=['Delay trades completeness for latency and state.', 'Cover most late data.', 'Correct the rest in batch.'],
         code='''p99, p999 = 8, 20
print("watermark", p99 + 2, "min; batch correction for the rest")
''', notes={1: 'Trade-off :: Bigger delay = more state, later append output.'},
         tryit='Scenario 3.'),
    dict(level='a', tag='Output modes · sinks', title='Mode for each consumer',
         problem='<p>Dashboard (upsert DB) and lake (Parquet).</p>',
         inp='two sinks',
         approach=['File sinks support only append.', 'DB can upsert: update mode.', 'Two queries.'],
         code='''print({"dashboard": "update", "lake parquet": "append + watermark"})
''', notes={1: 'Files :: Append only.'},
         tryit='Scenario 1.'),
]

QUIZ = mix([
    dict(q='Beginner: Event time is…', options=['When Spark reads the row', 'The timestamp inside the record', 'Kafka offset', 'Batch id'], answer=1,
         why='When it happened.'),
    dict(q='Beginner: Which mode writes the whole result every batch?', options=['append', 'update', 'complete', 'overwrite'], answer=2,
         why='State grows.'),
    dict(q='Beginner: Watermark =', options=['min event time', 'max event time − delay', 'processing time', 'batch duration'], answer=1,
         why='Lab: 10:11 − 5 = 10:06.'),
    dict(q='Intermediate: append on an aggregation without a watermark?', options=['Works', 'Error: unsupported output mode', 'Writes nothing', 'Drops data'], answer=1,
         why='Windows never final.'),
    dict(q='Intermediate: With a watermark, when is a window written in append mode?', options=['Immediately', 'When the watermark passes its end', 'Never', 'Each batch'], answer=1,
         why='Exactly once.'),
    dict(q='Intermediate: update mode writes…', options=['All windows', 'Windows changed in this batch', 'Final windows', 'Nothing'], answer=1,
         why='Good for upserts.'),
    dict(q='Advanced: Very late 7777 order with a watermark?', options=['Added', 'Dropped (numRowsDroppedByWatermark=1)', 'Error', 'Buffered'], answer=1,
         why='Window already final.'),
    dict(q='Advanced: Is a watermark an exact cut-off?', options=['Yes', 'No: older data may still be counted until state is removed', 'Only in append', 'Only for joins'], answer=1,
         why='10:02 (999) was still counted.'),
])

REVISION = [
    'Group by event time with <code>window()</code>; late data updates the right window.',
    'Watermark = max event time − delay; set with <code>withWatermark</code>.',
    'complete: all rows; update: changed rows; append: final rows only.',
    'append + aggregation needs a watermark (else UNSUPPORTED_OPERATION).',
    'Lab: 10:00 window emitted once as 1419 when watermark reached 10:06.',
    'Very late row dropped (1); without watermark 1419 → 9196.',
    'Watermarks bound state (5 → 2 rows) and add append latency.',
]
FAQ = [
    ('Does the watermark use the latest event or the slowest partition?', 'By default the global watermark uses the minimum across multiple watermarks (multipleWatermarkPolicy=min) and the max event time per stream.'),
    ('Can I use processing time instead?', 'Yes, current_timestamp() windows, but late data then lands in the wrong window.'),
    ('Why did the last batch have no new data?', 'Spark runs a no-data batch to advance the watermark and emit or evict state.'),
    ('Does update mode work with file sinks?', 'No, files support append only; use foreachBatch or a table format for upserts.'),
    ('Is the delay in processing time?', 'No, it is in event time: “5 minutes behind the latest event time seen”.'),
]

PRACTICE_INTRO = 'Programs about windows, watermarks and modes.'
PROBLEMS = [
    dict(level='easy', title='Watermark', stmt='Watermark for max event 10:22, delay 5.', inp='22, 5',
         code='''print(f"10:{22 - 5:02d}")
''', explain='10:17.'),
    dict(level='easy', title='Window start', stmt='5-min window of 10:13.', inp='13',
         code='''print(13 // 5 * 5)
''', explain='10:10.'),
    dict(level='easy', title='Late?', stmt='Is a 10:03 event older than watermark 10:17?', inp='3, 17',
         code='''print(3 < 17)
''', explain='Yes: may be dropped.'),
    dict(level='medium', title='Final windows', stmt='Windows final at watermark 10:11.', inp='starts 0,5,10',
         code='''print([w for w in (0, 5, 10) if w + 5 <= 11])
''', explain='10:00 and 10:05.'),
    dict(level='medium', title='Windowed sums', stmt='Sum per 5-min window.', inp='(minute, amount)',
         code='''from collections import defaultdict
s = defaultdict(int)
for m, a in [(1, 100), (2, 200), (6, 300), (3, 70)]:
    s[m // 5 * 5] += a
print(dict(s))
''', explain='Late 10:03 joins 10:00.'),
    dict(level='medium', title='Mode rows', stmt='Rows written per mode.', inp='5 windows, 2 changed, 1 final',
         code='''print({"complete": 5, "update": 2, "append": 1})
''', explain='Different contracts.'),
    dict(level='business', title='State saved', stmt='Windows kept for 30 days of 5-min windows without a watermark.', inp='30 days',
         code='''print(30 * 24 * 12)
''', explain='8,640 per key, and growing.'),
    dict(level='business', title='Latency of final numbers', stmt='Delay before a window is final.', inp='window 5, watermark 15 min',
         code='''print(5 + 15, "minutes after the window starts (at least)")
''', explain='Append latency.'),
]

SCN_INTRO = 'Watermarks and output modes are favourite advanced streaming questions.'
SCENARIOS = (
    scn('Any company · Spark', 'Fresher', '“Event time vs processing time”',
        'Explain the difference.',
        'why it matters?',
        '<p>Event time is when the event happened (in the data); processing time is when Spark sees it. Grouping by event time puts late events in the correct window; grouping by processing time is simpler but wrong when data is delayed.</p>', 'Ignoring late data.') +
    scn('Data engineering', 'Mid-level', '“What is a watermark?”',
        'Explain watermarks.',
        'effect on state?',
        '''<ul>
          <li>max event time − allowed delay; set with withWatermark.</li>
          <li>Windows older than it are finalised and removed from state.</li>
          <li>In my test a very late row was dropped and state stayed at 2 rows.</li>
        </ul>''', 'Saying it delays processing by the delay.') +
    scn('Data engineering', 'Mid-level', 'Append mode error',
        'append on a windowed count fails.',
        'why and fix?',
        '''<ol>
          <li>Append writes rows once; without a watermark nothing is ever final.</li>
          <li>Add withWatermark on the event-time column before groupBy.</li>
          <li>Or use update mode with an upserting sink.</li>
        </ol>''', 'Switching to complete mode on a file sink.') +
    scn('Platform', 'Senior', 'Late data policy',
        'Define a late-data policy for all streaming aggregates.',
        'policy?',
        '''<ul>
          <li>Watermark from measured lateness percentiles.</li>
          <li>Track numRowsDroppedByWatermark.</li>
          <li>Raw events always landed; batch corrections for very late data.</li>
        </ul>''', 'Huge watermarks to never drop data.')
)
