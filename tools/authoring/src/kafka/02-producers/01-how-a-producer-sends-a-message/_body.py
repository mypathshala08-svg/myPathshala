import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from kafkakit import *
C = 'l21_send.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('Your code said “sent” after 1 millisecond. Was anything actually sent?',
    'No. In our lab <code>produce()</code> returned in about 1 ms, but the broker confirmed each record about 60 ms later. In between, your record travels through six layers you never see. This lesson opens all of them.',
    ['Why <code>produce()</code> is a promise, not a delivery.',
     'Where your record waits, and how long it may wait before Kafka gives up.',
     'The exact error you get when the broker cannot be reached.'])
cmap = concept_map('Concept map. Beginner: produce, callback, flush. Intermediate: serializer, partitioner, record accumulator, sender thread, timeouts. Advanced: batching, acks, idempotence, transactions.',
    [[('pr', 'produce()', 'returns at once', None), ('cb', 'Delivery callback', 'success or error', None), ('fl', 'flush()', 'wait for all', None)],
     [('se', 'Serializer', 'object → bytes', None), ('pa', 'Partitioner', 'Lesson 2.2', B + '02-producers/02-keys-and-partitioners/'), ('ac', 'Accumulator + sender', 'batches + I/O thread', None), ('to', 'Timeouts', 'message/delivery', None)],
     [('ba', 'Batching + compression', 'Lesson 2.3', B + '02-producers/03-batching-and-compression/'), ('ak', 'acks', 'Lesson 2.4', B + '02-producers/04-acks-and-durability/'), ('id', 'Idempotence', 'Lesson 2.5', B + '02-producers/05-idempotent-producer-and-retries/')]],
    [('pr', 'se'), ('pr', 'ac'), ('cb', 'to'), ('ac', 'ba'), ('to', 'ak'), ('cb', 'id')],
    {'pr', 'cb', 'fl', 'se', 'ac', 'to'},
    '<b>Builds on:</b> Module 1, especially <a href="../../01-introduction/04-topics-partitions-and-offsets/">1.4</a>. <b>Next:</b> <a href="../02-keys-and-partitioners/">2.2 Keys and partitioners</a>.')
whw = why_how_where(
    'Sending one network request per record would be slow. Producers queue records and send them in batches, in the background.',
    'produce() serialises, picks a partition and appends to an in-memory batch; a background thread sends batches to partition leaders and calls your callback with the result.',
    'Every app that writes to Kafka: order services, payment gateways, log shippers, IoT gateways.',
    'Do not treat produce() as “saved”. If the app exits before flush(), queued records are lost.')

layers = [('cart', 'your code'), ('gear', 'serializer'), ('chart', 'partitioner'), ('disk', 'accumulator'), ('phone', 'sender thread'), ('bell', 'callback')]
sc_ = ''.join(box(14 + k * 104, 30, 92, 70, 'acc' if k in (0, 5) else 'card', rx=8) + icon(ic, 14 + k * 104 + 34, 38, 1.0) + t(14 + k * 104 + 46, 82, nm, 8, bold=True) + (arrow(106 + k * 104, 65, 118 + k * 104, 65, 'acc', 1.4) if k < 5 else '') for k, (ic, nm) in enumerate(layers))
sc_ += t(166, 122, '≈ 1 ms: produce() returns here ↑ (in your thread)', 7.8, 'acc', bold=True) + t(474, 122, '≈ 60 ms later (background thread)', 7.8, 'green', bold=True)
scene_svg = scene('The six stages of sending a record: your code, serializer, partitioner, record accumulator, sender thread, and the delivery callback. produce() returns after about 1 ms; the callback arrives about 60 ms later.', sc_,
                  'Sending is a <tspan font-weight="700" class="s-acc">pipeline</tspan>, not one function call.')
dialogue = '''K> Sir, I printed “order sent” right after <code>produce()</code>. But some orders never reached Kafka when the pod restarted.
A> Because <code>produce()</code> only puts the record in a queue inside your process. The real sending happens later, on a background thread. If your program exits first, those records die with it.
R> So how do we know a record really arrived?
A> The <b>delivery callback</b>. Kafka calls it with the partition and offset on success, or with an error. Let’s time every stage on our cluster.'''

lv = '''
LEVELS> The producer at three levels
L1> A post office counter
      <ul>
        <li>You drop a letter in the box (<code>produce</code>) and walk away. The postman collects many letters, sorts them by route (partition) and delivers them in one trip (batch).</li>
        <li>Later you get an SMS: “delivered” or “failed” (the callback).</li>
      </ul>
L2> The six stages
      <ul>
        <li><b>Serializer</b>: key and value objects → bytes (JSON, string, Avro…).</li>
        <li><b>Partitioner</b>: chooses the partition (Lesson 2.2).</li>
        <li><b>Record accumulator</b>: per-partition batches in memory, limited by a buffer (Java <code>buffer.memory</code>, librdkafka <code>queue.buffering.max.kbytes</code>).</li>
        <li><b>Sender thread</b>: sends ready batches to each partition’s <b>leader</b>, retries on retriable errors.</li>
        <li><b>Callback / future</b>: success with partition + offset, or an error.</li>
      </ul>
L3> Timeouts and back-pressure
      <ul>
        <li>A record may wait, be retried and be resent until a total deadline: Java <code>delivery.timeout.ms</code> (default 120 s), librdkafka <code>message.timeout.ms</code> (default 300 s). Then you get an error such as <code>_MSG_TIMED_OUT</code>.</li>
        <li><code>request.timeout.ms</code> limits one network request; a timeout there triggers a retry, not a failure.</li>
        <li>If the buffer is full, Java blocks up to <code>max.block.ms</code>; librdkafka raises <code>BufferError</code> immediately: call <code>poll()</code> and try again.</li>
      </ul>
/LEVELS
'''
DIS = figure('Dissection of a delivery report from our lab: key o1, partition 2, offset 0, latency 60 milliseconds, and the produce call that returned after 0.96 milliseconds.',
    t(16, 22, 'One record, two moments', 8.6, 'ink', anchor='start', bold=True) +
    fields(16, 34, [('produce("orders-21", key="o1", ...)', 'card', 1), ('returned after 0.96 ms', 'acc', 2)]) +
    fields(16, 74, [('callback', 'green', 3), ('key o1', 'card', None), ('partition 2', 'blue', 4), ('offset 0', 'blue', 5), ('latency 60.0 ms', 'amber', 6)]) +
    legend(16, 128, [(1, 'produce()', 'serialise + partition + append to a batch; no network yet'),
                     (2, 'Return', 'your thread is free almost immediately'),
                     (3, 'Callback', 'runs inside poll() or flush() when the leader answers'),
                     (4, 'Partition', 'chosen by the key hash'),
                     (5, 'Offset', 'assigned by the leader; proof it is stored'),
                     (6, 'Latency', 'queue wait + linger + network + replication (acks)')], size=8, gap=15, w=110),
    h=232, caption='Real numbers from our lab run, dissected.')
extra = '''

  <h3>Dissect a delivery report</h3>
''' + DIS + '''

  <h3>The producer settings you will meet first</h3>
''' + table(['Setting (Java name / librdkafka name)', 'Default', 'What it controls'], [
    ['bootstrap.servers', 'none', 'first brokers to contact'],
    ['key.serializer, value.serializer', 'Java: required', 'object → bytes (Python: you pass bytes or str)'],
    ['acks', 'all', 'how many replicas must confirm (Lesson 2.4)'],
    ['linger.ms', 'Java 5 ms (since 4.0), librdkafka 5 ms', 'how long to wait to fill a batch (Lesson 2.3)'],
    ['batch.size / batch.num.messages', '16 KB / 10,000', 'maximum batch size'],
    ['enable.idempotence', 'true', 'no duplicates on retry (Lesson 2.5)'],
    ['delivery.timeout.ms / message.timeout.ms', '120 s / 300 s', 'total time before giving up on a record'],
    ['request.timeout.ms', '30 s', 'one request; then retry'],
    ['buffer.memory / queue.buffering.max.kbytes', '32 MB / 1 GB', 'memory for queued records'],
], minw=640)

types_html = table(['Sending style', 'Code (Python)', 'Throughput', 'When'], [
    ['Fire-and-forget', '<code>produce(...)</code>, ignore result', 'highest', 'metrics where loss is acceptable'],
    ['Asynchronous with callback', '<code>produce(..., callback=cb)</code> + <code>poll(0)</code>', 'high', 'the normal way'],
    ['Synchronous', '<code>produce(...)</code> then <code>flush()</code> each time', 'very low', 'tests, rare critical writes'],
], minw=600) + table(['Error type', 'Example', 'Producer does'], [
    ['Retriable', 'NOT_LEADER_OR_FOLLOWER, NOT_ENOUGH_REPLICAS, network timeout', 'retries automatically until the deadline'],
    ['Non-retriable', 'RECORD_TOO_LARGE, authorization failed, invalid config', 'fails the record at once'],
    ['Local', '_MSG_TIMED_OUT, queue full (BufferError)', 'reports to your callback / raises'],
], minw=600)
warn = 'Always call <code>flush()</code> (with a timeout) before your program exits, and call <code>poll(0)</code> regularly while producing so callbacks run and the queue drains. Never write “sent!” to a database before the callback says success.'

steps = [
    ('Step 1 · produce() returns before anything is sent',
     code('python', 'l21_send.py', 'p = Producer({"bootstrap.servers": BS, "linger.ms": 5})\nfor i in range(1, 6):\n    p.produce("orders-21", key=f"o{i}", value=json.dumps({...}), callback=cb)\n    print("produce() returned after ... ms (in queue:", len(p), ")")\nprint("callbacks so far:", len(events))\np.flush(10)', sec('== 1)', '== 2)')),
     'Each <code>produce()</code> returned in about 1 ms and the queue grew to 5. <b>Zero</b> callbacks had run. Only <code>flush()</code> waited for the network: 61 ms later all five came back with partition and offset. Callbacks arrive per partition batch, not in send order (o1, o3, o4 then o2, o5).'),
    ('Step 2 · Latency of many records',
     code('python', 'l21_send.py', 'for i in range(200):\n    p.produce("orders-21", key=f"x{i}", value="v", callback=lambda e, m: lat.append(m.latency()))\n    p.poll(0)\np.flush()', sec('== 2)', '== 3)')),
     '<code>m.latency()</code> is the time from produce to acknowledgement. Median 34 ms, p99 56 ms on our Docker lab with <code>acks=all</code> (3 replicas). Production clusters on real disks and networks are usually a few milliseconds.'),
    ('Step 3 · A failed send',
     code('python', 'l21_send.py', 'bad = Producer({"bootstrap.servers": "localhost:19999", "message.timeout.ms": 3000})\nbad.produce("orders-21", key="o9", value="lost?", callback=...)\nbad.flush(10)', sec('== 3)')),
     '<code>produce()</code> did not raise any error. After the 3-second deadline the callback reported <code>_MSG_TIMED_OUT</code>. Without a callback you would never know this record was lost.'),
]

see = [term([('produce() o1 returned after 0.96 ms (in queue: 1)', W), ('produce() o5 returned after 1.11 ms (in queue: 5)', W), ('callbacks so far: 0', Y)], size=6.8),
       term([('flush() done after 61.2 ms', G), ('callback o1 -> partition 2 offset 0', W), ('latency 60.0 ms', W)], size=7.0),
       term([('200 records: median 34.3 ms', W), ('p99 56.2 ms', W)], size=7.4),
       term([('after 3.0 s the callback said:', W), ('Local: Message timed out', RD)], size=7.4)]
def pipe(hi, note):
    o = ''.join(opbox(6 + k * 58, 46, n, '', 'acc' if k == hi else 'card', 52, 28) + (arrow(58 + k * 58, 60, 64 + k * 58, 60, 'ink3', 1) if k < 5 else '') for k, n in enumerate(['code', 'serial', 'partit.', 'batch', 'sender', 'cb']))
    return t(180, 14, note, 9, bold=True) + o
B1 = [pipe(3, 'Records wait in the batch') + cap('Queue = 5, nothing sent yet.', '', 'amber', y=144, h=30),
      pipe(4, 'Sender ships the batch') + cap('Leader answers → callbacks.', '', 'green', y=144, h=30),
      pipe(4, 'Latency = wait + network + acks') + cap('Median 34 ms in the lab.', '', 'blue', y=144, h=30),
      pipe(5, 'Deadline passed') + cap('Error only in the callback.', '', 'red', y=144, h=30)]
two = anim_two('How a producer sends', 'From call to confirmation', 'Real outputs from the lab', 'Where the record is', see, B1,
               ['Queued.', 'Delivered.', 'Latency.', 'Failure.'], ['Accumulator.', 'Sender.', 'Timing.', 'Timeout.'])
pe = peel('Record o1, layer by layer', 'From produce() to callback. (Our run.)',
    [('produce()', ''), ('Serializer', ''), ('Partitioner', ''), ('Accumulator', ''), ('Sender + leader', ''), ('Callback', '')],
    [['produce()', 'key "o1", value JSON', 'returns in 0.96 ms', ''], ['Serializer', 'str → UTF-8 bytes', 'Kafka stores bytes only', ''],
     ['Partitioner', 'hash(key) → partition 2', '(librdkafka default', 'in this script)'], ['Accumulator', 'append to P2 batch', 'wait up to linger.ms=5', 'queue length 5'],
     ['Sender + leader', 'Produce request to leader', 'replicas copy (acks=all)', 'offset 0 assigned'], ['Callback', 'during flush()/poll()', 'P2, offset 0, 60 ms', '“now it is safe”']],
    ['Call.', 'Bytes.', 'Partition.', 'Batch.', 'Network.', 'Confirm.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'Orders lost on deploy', 'Exiting without flush. (Typical.)', ('flush on shutdown', 'Queued records are lost if the process exits before flush()'), [
    ('New version deployed', 'pods stopped quickly', 'SIGTERM.', 'blue'), ('2,000 orders in queue', 'never sent', 'No error seen.', 'red'),
    ('Customers charged, no order', 'support calls', 'Costly.', 'red'), ('Fix: handle SIGTERM', 'producer.flush(30)', 'Then exit.', 'green'),
    ('Callbacks to DB only on success', 'idempotent writes', 'Safe.', 'blue')], ['Deploy.', 'Queue.', 'Impact.', 'Flush.', 'Safe.'], 'scenario-flush') + \
       five('Real-time scenario 2', 'BufferError at peak', 'Back-pressure when the queue is full. (Typical.)', ('Back-pressure', 'When the producer buffer is full, slow down: poll and retry'), [
    ('Sale traffic 10×', 'broker slower', 'Queue fills.', 'blue'), ('BufferError raised', 'librdkafka queue full', 'App crashes.', 'red'),
    ('Catch BufferError', 'poll(0.1), retry', 'Natural pacing.', 'green'), ('Watch queue length', 'len(producer) metric', 'Alert early.', 'green'),
    ('Scale brokers or batch', 'linger, compression', 'Lesson 2.3.', 'blue')], ['Peak.', 'Error.', 'Retry.', 'Watch.', 'Fix.'], 'scenario-buffer') + \
       five('Real-time scenario 3 · advanced', 'Silent timeouts', 'Records expiring without anyone noticing. (Typical.)', ('Delivery timeout', 'Records fail after message.timeout.ms; only the callback knows'), [
    ('Broker down 6 minutes', 'librdkafka timeout 5 min', 'Some records expire.', 'blue'), ('No callback in code', 'nobody sees errors', 'Silent loss.', 'red'),
    ('Add callback + metric', 'count delivery errors', 'Dashboards.', 'green'), ('Dead-letter store', 'save failed records', 'Replay later.', 'green'),
    ('Tune deadline', 'longer for critical data', 'Know the default.', 'blue')], ['Outage.', 'Silent.', 'Measure.', 'Store.', 'Tune.'], 'scenario-timeout')
assemble(HERE, h2_story='“Sent” is not the same as “stored”', hook_html=hk,
    narration='TiffinGo’s order service logs “order sent to Kafka” and moves on. After a deployment, the finance team finds 2,000 paid orders that never reached the kitchen. Kabir is asked to find out why.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='How a producer sends a message',
    formal='A Kafka <b>producer</b> is a client that publishes records to topic partitions. Sending is <b>asynchronous</b>: <code>send</code>/<code>produce</code> serialises the key and value, determines the partition, and appends the record to a per-partition batch in the <b>record accumulator</b>. A background <b>sender (I/O) thread</b> transmits ready batches as Produce requests to each partition leader, handles retries for retriable errors, and completes each record’s future or invokes its <b>delivery callback</b> with the assigned offset or an error. A record that cannot be acknowledged within the delivery timeout fails.',
    simple='When you send, the producer only puts your record in a queue and returns. A background worker sends records in groups to the right broker and later tells you, through a callback, whether each one was saved.',
    term_rows=[('Delivery callback', 'Called with result per record.'), ('Serializer', 'Turns objects into bytes.'), ('Record accumulator', 'In-memory batches per partition.'), ('Sender thread', 'Background network worker.'), ('flush()', 'Wait until the queue is empty.'), ('poll()', 'Serve callbacks (librdkafka).'), ('Latency', 'Produce to acknowledgement time.'), ('Delivery timeout', 'Total time before giving up.')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('produce()/send() means the record is saved.', 'It only queues the record; the callback confirms storage.', 'Step 1: 5 produced, 0 callbacks until flush().'),
               ('If sending fails, produce() raises an error.', 'Network failures appear later in the callback.', 'Step 3: _MSG_TIMED_OUT after 3 s, no exception.'),
               ('Callbacks arrive in the order you sent.', 'They arrive per partition batch.', 'Step 1: o1, o3, o4, then o2, o5.')],
    exam='“Explain the Kafka producer’s send path.” send() → serializer → partitioner → record accumulator (batch per partition) → sender thread → Produce request to the leader → acks → callback/future with offset or error; retries for retriable errors until delivery.timeout.ms; flush()/close() before exit.',
    types_h2='Sending styles and errors', types_html=types_html, warn=warn,
    steps_h2='Timing every stage', steps_intro='All outputs are real: Kafka 4.4.0 (3 brokers), Python <code>confluent-kafka</code> 2.16.1. Topic <code>orders-21</code>, 3 partitions, RF 3. Script: <code>jobs/m2/l21_send.py</code>.',
    steps=steps, two=two, peel_intro='Now peel one record layer by layer.', peel_html=pe,
    scen_intro='Three live scenarios: lost orders on deploy, a full buffer, and silent timeouts.', scen=scen,
    uc_h2='Producers at work', ucs=[uc_('pay', 'gateway', 'green', '1. Payment gateway', 'Writes payment events and only confirms to the user after the callback succeeds.', ['Payment', '*callback', 'Confirm']),
        uc_('logs', 'agents', 'blue', '2. Log shippers', 'Agents batch thousands of log lines per request; small loss acceptable.', ['Servers', '*batches', 'Kafka']),
        uc_('IoT', 'gateway', 'violet', '3. IoT gateways', 'Buffer readings while the network is down; deadline decides when to drop.', ['Sensors', '*buffer', 'Kafka']),
        uc_('shop', 'checkout', 'acc', '4. Checkout service', 'Flushes on shutdown so no order event is lost during deploys.', ['Order', '*flush', 'Kafka']),
        uc_('ride', 'GPS', 'blue', '5. Driver location', 'Fire-and-forget: a lost GPS point is replaced 2 seconds later.', ['GPS', '*async', 'Kafka'])],
    uc_note='Examples are simplified descriptions of common patterns.',
    pre='<b>Before you start:</b> Module 1, especially <a href="../../01-introduction/04-topics-partitions-and-offsets/">1.4</a> and the lab from <a href="../../01-introduction/06-two-real-time-projects-vm-and-colab/">1.6</a>.')
