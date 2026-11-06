import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from sparkkit import *
C = 'l93_watermark.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)

def timeline(x, y, w, events, wm=None, t0=0, t1=25, label=''):
    """events: list of (minute, tone)."""
    sx = lambda m: x + (m - t0) / (t1 - t0) * w
    o = fill(x, y - 0.6, w, 1.2, '#8A94A0', rx=0)
    for m in range(t0, t1 + 1, 5):
        o += fill(sx(m) - 0.6, y - 3, 1.2, 6, '#8A94A0', rx=0) + t(sx(m), y + 14, f'10:{m:02d}', 6.4, 'ink2')
    for m, tone in events:
        o += box(sx(m) - 5, y - 15, 10, 10, tone, rx=5)
    if wm is not None:
        o += fill(sx(wm) - 0.9, y - 26, 1.8, 30, 'red', rx=0) + t(sx(wm), y - 30, f'watermark 10:{wm:02d}', 6.6, 'red', bold=True)
    if label:
        o += t(x, y - 40, label, 7.2, 'ink2', anchor='start', bold=True)
    return o

# ---------------------------------------------------------------- story
sc_ = (timeline(20, 92, 340, [(1, 'green'), (2, 'green'), (4, 'green'), (6, 'green'), (11, 'green'), (16, 'green'), (3, 'acc')], wm=11, label='event time (when the order happened)') +
       box(400, 12, 232, 132, 'card') + t(516, 30, 'Measured (5 min windows)', 8.6, bold=True) +
       ''.join(t(412, 52 + k * 16, s, 7.2, c, anchor='start', mono=True) for k, (s, c) in enumerate([
           ('append w/o watermark: ERROR', 'red'), ('complete: re-emits all', 'amber'),
           ('update: only changed', 'green'), ('append+wm: final once', 'green'),
           ('very late 7777: dropped', 'green'), ('state 5 → 2 rows', 'green')])))
scene_svg = scene('Events carry the time they happened, but arrive late and out of order. We fed five micro-batches of orders, some late, into a 5-minute window aggregation and compared complete, update and append output modes with and without a 5-minute watermark.', sc_,
                  'A watermark tells Spark <tspan font-weight="700" class="s-acc">how late is too late</tspan>.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“The 10:00 numbers changed at 10:25”</h2>
  <div class="story">
    <p class="narration">TiffinGo’s live dashboard showed revenue per 5-minute window. Rider phones without network uploaded orders late, so the 10:00 window kept changing long after 10:05. Finance asked a simple question: when is a window <b>final</b>?</p>

{scene_svg}

K> Sir, why not group by the time the event reaches Kafka? Then nothing is late.
A> Then a phone that was offline would put a 10:02 order into the 10:25 window: wrong revenue. We group by <b>event time</b>, the time inside the record. Late data is normal; the question is how long to wait for it.
R> And Spark waits forever?
A> Without a <b>watermark</b>, yes: it keeps every window in state and can update any of them. With a watermark it can finalise windows, drop data that is too late, and free memory. Today we see this batch by batch, in all three output modes. All outputs are real (PySpark 4.3.0).
  </div>
</section>
'''

lv = '''
LEVELS> Event time at three levels
L1> Exam papers by post
      <ul>
        <li>Papers are dated when written (event time) but arrive by post over days (processing time).</li>
        <li>The examiner announces: “I will accept papers up to 5 days after the latest date I have seen.” That rule is the watermark. Results are published once a date is safely past it.</li>
      </ul>
L2> The API
      <ul>
        <li><code>df.withWatermark("event_time", "5 minutes")</code> before a stateful operation.</li>
        <li><code>groupBy(F.window("event_time", "5 minutes"))</code> for event-time windows.</li>
        <li><code>writeStream.outputMode("append" | "update" | "complete")</code>.</li>
      </ul>
L3> What the lab showed
      <ul>
        <li>append on an aggregation without watermark: <code>STREAMING_OUTPUT_MODE.UNSUPPORTED_OPERATION</code>.</li>
        <li>With the watermark, each window was emitted once, when the watermark passed its end; state shrank to 2 rows.</li>
        <li>A 10:03 order arriving after the 10:00 window was finalised was dropped (<code>numRowsDroppedByWatermark</code> = 1); without a watermark it changed 1419 to 9196.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Output modes, event time and watermarks</h2>
''' + def_block(
    '<b>Event time</b> is the timestamp embedded in a record, as opposed to processing time when Spark sees it. Event-time aggregations such as <code>groupBy(window("event_time", "5 minutes"))</code> keep per-window <b>state</b> across micro-batches so late, out-of-order records update the right window. A <b>watermark</b>, defined with <code>withWatermark(col, delay)</code>, is computed as the maximum event time seen minus the delay; Spark guarantees that records newer than the watermark are processed, may drop records older than it, and removes state for windows that end before it. The <b>output mode</b> controls what each micro-batch writes: <b>complete</b> rewrites the whole result table, <b>update</b> writes only rows changed in this batch, and <b>append</b> writes only rows that will never change again, which for aggregations requires a watermark.',
    'Event time is when something really happened. Spark keeps window results in memory so late events can still be added. A watermark says “I will wait this long for late data”: after that a window is final, it can be written once, and its memory is freed. Output modes decide whether you write everything, only changes, or only final rows.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Event time', 'Time inside the record.'),
    ('Processing time', 'When Spark processes it.'),
    ('Late data', 'Arrives after newer events.'),
    ('Window', 'Time bucket, e.g. 5 minutes.'),
    ('Watermark', 'max event time − delay.'),
    ('complete', 'Write the whole result each batch.'),
    ('update', 'Write rows changed this batch.'),
    ('append', 'Write rows that are final.'),
]) + '''

  <h3>Output modes for a windowed aggregation</h3>
''' + table(['Mode', 'Writes each batch', 'Needs watermark?', 'State', 'Lab'], [
    ['complete', 'All windows', 'No', 'Grows forever', '5 rows written in batch 4'],
    ['update', 'Changed windows', 'No (but advised)', 'Grows unless watermark', '2 rows in batch 4'],
    ['append', 'Final windows only', 'Yes', 'Bounded', 'Each window once; state 2'],
], minw=620) + lv + '''
EXAM> “What is a watermark?” A threshold on event time, max(event_time) − allowed delay, that tells Spark how long to wait for late data. Windows ending before it are finalised: emitted in append mode and removed from state; records older than it may be dropped. It bounds state for streaming aggregations, deduplication and stream-stream joins, and is required for append mode with aggregations.
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Which sink supports which mode</h2>
''' + table(['Sink', 'append', 'update', 'complete'], [
    ['Files (Parquet/JSON)', 'Yes', 'No', 'No'],
    ['Kafka', 'Yes', 'Yes', 'Yes'],
    ['foreachBatch', 'Yes', 'Yes', 'Yes'],
    ['Delta / Iceberg table', 'Yes', 'via foreachBatch MERGE', 'Yes (overwrite)'],
    ['console / memory', 'Yes', 'Yes', 'Yes'],
], minw=560) + '''
WARN> A watermark is a <b>lower bound</b> on what is kept, not an exact cut-off. In our run a 10:02 order arrived in the same batch that closed its window and was still counted, but a 10:03 order arriving one batch later was dropped. And append mode adds latency: a window is written only after the watermark passes its end, so the 10:00 window appeared two batches after its last event. Pick the delay from how late your data really is, not from how fast you want results.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Five batches, three output modes</h2>
  <p>All outputs are real: PySpark 4.3.0, <code>local[2]</code>, UTC. One JSON file per micro-batch (<code>maxFilesPerTrigger=1</code>, files ordered by time) so every run sees the same batches. <code>foreachBatch</code> prints what each mode writes; progress shows the watermark and the state store.</p>
  <ul>
    <li>Batch 0: 10:01 (100), 10:02 (200), 10:04 (50)</li>
    <li>Batch 1: 10:06 (300), <b>10:03 (70) late</b>, 10:11 (20)</li>
    <li>Batch 2: 10:16 (10), <b>10:02 (999) late</b>, 10:12 (40)</li>
    <li>Batch 3: 10:22 (5)</li>
    <li>Batch 4: <b>10:03 (7777) very late</b>, 10:24 (1)</li>
  </ul>
''' + stepper([
    ('Step 1 · complete mode',
     code('python', 'l93_watermark.py', 'w5 = F.window("event_time", "5 minutes")\nplain = ev.groupBy(w5).agg(F.sum("amount").alias("revenue"))\nplain.writeStream.outputMode("complete").foreachBatch(show).start()', sec('== 1', '== 2')),
     'Every batch rewrites <b>all</b> windows. Late rows land in the right window: 10:03 (70) raised 10:00 from 350 to 420. Without a watermark the very late 7777 also went in: <b>1419 → 9196</b>. State rows only grow (1 → 5): fine for 5 windows, fatal for a stream that runs for months.'),
    ('Step 2 · update mode',
     code('python', 'l93_watermark.py', 'plain.writeStream.outputMode("update").foreachBatch(show).start()', sec('== 2', '== 3')),
     'Same state, but each batch writes only the windows that <b>changed</b>: batch 3 wrote just 10:20. Good for sinks that can upsert (a database keyed by window). Still no watermark, so state still grows and very late data is still accepted.'),
    ('Step 3 · append without a watermark',
     code('python', 'l93_watermark.py', 'plain.writeStream.outputMode("append").foreachBatch(show).start()', sec('== 3', '== 4')),
     'Refused before any data is read. Append means “write a row once, never change it”, but without a watermark Spark can never know a window is final.'),
    ('Step 4 · append with a 5-minute watermark',
     code('python', 'l93_watermark.py', 'wm = ev.withWatermark("event_time", "5 minutes").groupBy(w5).agg(F.sum("amount").alias("revenue"))\nwm.writeStream.outputMode("append").foreachBatch(show).start()', sec('== 4', '== 5')),
     'Batches 0 and 1 wrote <b>nothing</b>: no window was final yet. After batch 1 the max event time was 10:11, so the watermark became <b>10:06</b> and the 10:00–10:05 window was emitted in batch 2 as <b>1419</b>, once. Each later batch finalised one more window. In batch 4 the 7777 order (10:03) was older than the watermark (10:17) and its window was gone: <b>dropped late 1</b>. State stayed at 2–3 rows.'),
    ('Step 5 · update with a watermark',
     code('python', 'l93_watermark.py', 'wm.writeStream.outputMode("update").foreachBatch(show).start()', sec('== 5')),
     'The best of both for upserting sinks: windows are written as soon as they change (low latency), late data within 5 minutes still updates them, very late data is dropped, and old windows leave the state. Compare batch 4 here (10:20 → 6, 7777 ignored) with batch 4 in Step 2.'),
]) + '''
</section>
'''

# ---------------------------------------------------------------- two-view animation
see = [
    term([('complete b1: 10:00=420 10:05=300 10:10=20', W), ('complete b4: 10:00=9196 (7777 in)', RD), ('state rows: 1 3 4 5 5', Y)], size=7.0),
    term([('update b3: [10:20=5]', G), ('update b4: [10:00=9196, 10:20=6]', Y)], size=7.2),
    term([('append, no watermark:', W), ('STREAMING_OUTPUT_MODE', RD), ('  .UNSUPPORTED_OPERATION', RD)], size=7.4),
    term([('append b0/b1: []', W), ('b2: 10:00=1419  wm 10:06', G), ('b4: 10:10=60  dropped late 1', G)], size=7.2),
]
B1 = [
    t(180, 14, 'complete: everything, every batch', 9.4, bold=True) + timeline(20, 92, 320, [(1, 'green'), (2, 'green'), (4, 'green'), (6, 'green'), (11, 'green'), (3, 'acc')]) + cap('Late rows go to the right window.', '', 'amber', y=144, h=30),
    t(180, 14, 'update: only what changed', 9.4, bold=True) + ''.join(opbox(20 + k * 66, 50, f'10:{k * 5:02d}', 'changed' if k in (0, 4) else 'same', 'green' if k in (0, 4) else 'card', 60, 30) for k in range(5)) + cap('Good for upsert sinks.', '', 'green', y=144, h=30),
    t(180, 14, 'append needs “final”', 9.4, bold=True) + opbox(40, 50, 'no watermark', 'never final', 'red', 120, 32) + opbox(200, 50, 'watermark', 'final after wm', 'green', 120, 32) + cap('Spark refuses the first.', '', 'red', y=144, h=30),
    t(180, 14, 'Watermark = max event − 5 min', 9.4, bold=True) + timeline(20, 92, 320, [(1, 'green'), (6, 'green'), (11, 'green'), (16, 'green'), (22, 'green'), (3, 'red')], wm=17) + cap('Older windows emitted, then forgotten.', '', 'green', y=144, h=30),
]
see_caps = ['complete mode.', 'update mode.', 'append without watermark.', 'append with watermark.']
behind_caps = ['Event-time windows.', 'Changed rows only.', 'Why append needs a watermark.', 'Finalising and dropping.']
two = anim_two('Output modes and watermarks', 'When is a window final?', 'Real lab outputs', 'What Spark does', see, B1, see_caps, behind_caps)

e1 = (t(180, 22, 'Revenue per 5-min window', 9.4, bold=True) + t(180, 56, 'riders upload up to 10 min late', 8.4, 'ink2') + cap('Late data is normal.', '', 'blue', y=150, h=34))
e2 = (t(180, 22, 'Group by event time', 9.4, bold=True) + t(180, 56, 'not Kafka arrival time', 8.4, 'ink2') + cap('Correct windows.', '', 'green', y=150, h=34))
e3 = (t(180, 22, 'withWatermark 15 minutes', 9.4, bold=True) + t(180, 56, 'a bit above the real delay', 8.4, 'ink2') + cap('Safety margin.', '', 'green', y=150, h=34))
e4 = (t(180, 22, 'Dashboard: update mode', 9.4, bold=True) + t(180, 56, 'live numbers, upsert by window', 8.4, 'ink2') + cap('Fast.', '', 'green', y=150, h=34))
e5 = (t(180, 22, 'Finance: append mode', 9.4, 'acc', bold=True) + t(180, 56, 'final numbers, written once', 8.4, 'ink2') + cap('Two queries, two needs.', '', 'blue', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Live numbers and final numbers',
              'Choosing output modes. (Typical; behaviour from our lab.)',
              'Two modes', 'Use update mode for live dashboards and append with a watermark for final reports', [e1, e2, e3, e4, e5],
              ['Late data.', 'Event time.', 'Watermark.', 'Live.', 'Final.'],
              hid='scenario-modes')
b1 = (t(180, 22, 'Stream ran fine for 3 weeks', 9.4, bold=True) + t(180, 56, 'then batches got slower', 8.4, 'ink2') + cap('Then executors died.', '', 'blue', y=150, h=34))
b2 = (t(180, 22, 'State rows: 40 million', 9.4, bold=True) + t(180, 56, 'every window since day 1', 8.4, 'ink2') + cap('No watermark.', '', 'red', y=150, h=34))
b3 = (t(180, 22, 'Add withWatermark', 9.4, bold=True) + t(180, 56, 'needs a new checkpoint', 8.4, 'ink2') + cap('Plan the migration.', '', 'amber', y=150, h=34))
b4 = (t(180, 22, 'State stays small', 9.4, bold=True) + t(180, 56, '5 → 2 rows in our lab', 8.4, 'ink2') + cap('Bounded.', '', 'green', y=150, h=34))
b5 = (t(180, 22, 'Monitor numRowsTotal', 9.4, 'acc', bold=True) + t(180, 56, 'alert if it only grows', 8.4, 'ink2') + cap('Catch it early.', '', 'blue', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'The state that never shrank',
              'Unbounded state without a watermark. (Typical; state sizes from our lab.)',
              'Unbounded state', 'Without a watermark, aggregation state grows forever; add one and monitor state rows', [b1, b2, b3, b4, b5],
              ['Slower.', 'Huge state.', 'Watermark.', 'Bounded.', 'Monitor.'],
              hid='scenario-state')
u1 = (t(180, 22, 'A rider phone offline 2 hours', 9.4, bold=True) + t(180, 56, 'uploads 40 orders at once', 8.4, 'ink2') + cap('Watermark is 15 min.', '', 'blue', y=150, h=34))
u2 = (t(180, 22, 'Orders dropped as late', 9.4, bold=True) + t(180, 56, 'numRowsDroppedByWatermark = 40', 8.2, 'ink2') + cap('Revenue understated.', '', 'red', y=150, h=34))
u3 = (t(180, 22, 'Do not raise the delay to 2 h', 9.4, bold=True) + t(180, 56, 'state and latency grow 8x', 8.4, 'ink2') + cap('Wrong trade-off.', '', 'amber', y=150, h=34))
u4 = (t(180, 22, 'Also write raw events', 9.4, bold=True) + t(180, 56, 'to the lake, append, no agg', 8.4, 'ink2') + cap('Nothing is lost there.', '', 'green', y=150, h=34))
u5 = (t(180, 22, 'Nightly batch correction', 9.4, 'acc', bold=True) + t(180, 56, 'recompute yesterday from raw', 8.4, 'ink2') + cap('Fast + correct.', '', 'blue', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Very late data that matters',
              'Dropped rows and batch correction. (Typical.)',
              'Very late data', 'Keep a raw copy of events and correct aggregates in batch when data can be very late', [u1, u2, u3, u4, u5],
              ['Offline.', 'Dropped.', 'Not this.', 'Raw copy.', 'Correct.'],
              hid='scenario-verylate')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>When is a window final?</h2>
  <p>Left: real outputs. Right: what each mode and the watermark do.</p>
''' + two + '''
  <p>Three live scenarios follow: live vs final numbers, state that never shrank, and very late data.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Event time at work</h2>
''' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-blue" style="stroke:var(--blue)"/>' + t(60, 42, 'live', 12, 'blue', bold=True) + t(60, 58, 'update', 7.4, 'ink2'),
    '1. Live dashboards',
    'Per-minute counts in update mode, upserted into a serving table.',
    ['Events', '*update mode', 'Upsert']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-green" style="stroke:var(--green)"/>' + t(60, 42, 'final', 12, 'green', bold=True) + t(60, 58, 'append', 7.4, 'ink2'),
    '2. Final hourly tables',
    'Append mode with a watermark writes each hour once to the lake.',
    ['Events', '*append + watermark', 'Hourly table']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-violet" style="stroke:var(--violet)"/>' + t(60, 42, 'IoT', 12, 'violet', bold=True) + t(60, 58, 'devices', 7.4, 'ink2'),
    '3. Device telemetry',
    'Sensors buffer readings offline; event time keeps them in the right minute.',
    ['Buffered readings', '*event time', 'Correct minutes']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-acc" style="stroke:var(--track)"/>' + t(60, 42, 'SLA', 12, 'acc', bold=True) + t(60, 58, 'metrics', 7.4, 'ink2'),
    '4. Delivery SLAs',
    'Late-delivery rates per 15-minute window feed operations alerts.',
    ['Deliveries', '*windows', 'Alerts']) + '\n' + usecase(
    '<rect x="16" y="22" width="88" height="46" rx="6" class="s-card2"/>' + t(60, 42, 'audit', 12, 'acc', bold=True) + t(60, 58, 'late rows', 7.4, 'ink2'),
    '5. Late-data audits',
    'Dropped-row metrics are tracked to tune the watermark delay.',
    ['Progress metrics', '*dropped rows', 'Tune delay']) + '''
  <p class="muted">Examples are simplified.</p>
</section>
'''

pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> streaming basics in <a href="../01-streaming-concepts/">9.1</a>, sources and foreachBatch in <a href="../02-sources-and-sinks/">9.2</a>, dates and timestamps in <a href="../../06-transformations/04-string-and-date-functions/">6.4</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
