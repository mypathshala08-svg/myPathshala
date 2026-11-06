import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
BODY = body(HERE)
META = dict(module='02-producers', lesson='01-how-a-producer-sends-a-message', n='2.1', module_label='Module 2 · Producers',
    title='How a producer sends a message',
    desc='Inside the Kafka producer: serializer, partitioner, record accumulator, sender thread and delivery callback. Real Kafka 4.4 lab with confluent-kafka: produce() returns in about 1 ms while confirmation arrives about 60 ms later, latency percentiles, a failed send that only the callback reports, plus the first producer settings, error types and timeouts.',
    og_desc='produce() returned in 1 ms, the broker confirmed 60 ms later: the six stages of a Kafka producer, measured.',
    minutes=26, level='Intermediate',
    lead='When your code calls <code>produce()</code>, nothing has been sent yet. We time every stage of the <b>Kafka producer</b> on a real cluster, read a delivery report, and watch a failure that only the <b>callback</b> reveals. <b>All outputs are real.</b>',
    chips=['Kafka 4.4 + confluent-kafka', 'Callback vs return', 'Timeouts explained', 'Runs in your browser (Python)'])
MAIN = '''# A tiny producer model: queue in your thread, send + callback later
import time
queue, log = [], []
def produce(key, value, callback):
    queue.append((key, value, callback, time.perf_counter()))   # returns at once
def flush():
    while queue:                                                # the "sender thread"
        key, value, cb, t0 = queue.pop(0)
        log.append(value)
        cb(None, key, len(log) - 1, (time.perf_counter() - t0) * 1000)
def report(err, key, offset, ms):
    print("delivered", key, "offset", offset, f"after {ms:.3f} ms" if not err else err)
for i in range(1, 4):
    produce(f"o{i}", f"order {i}", report)
    print("produce() returned, queue =", len(queue))
flush()
'''
RUN = dict(heading='Run the code: queue now, deliver later', intro='<p>The producer’s two moments in a few lines. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('    queue.append((key, value, callback, time.perf_counter()))   # returns at once', 'produce() only queues the record.'),
          ('        cb(None, key, len(log) - 1, (time.perf_counter() - t0) * 1000)', 'The callback reports the offset: only now is it stored.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>. Then remove the flush() call.', code=None),
        dict(label='2 · Predict first: lost records', hint='<b>Predict first:</b> 5 queued, program exits without flush. How many stored?', code='queued, stored = 5, 0\nprint("lost:", queued - stored)\n'),
        dict(label='3 · Deadline', hint='Does a record waiting 310 s fail with the librdkafka default?', code='print(310_000 > 300_000)\n'),
        dict(label='4 · Percentile', hint='p99 of latencies.', code='lat = sorted([30, 31, 33, 34, 35, 36, 40, 56])\nprint(lat[int(0.99 * (len(lat) - 1))])\n'),
        dict(label='5 · Spot the error', hint='Queue full.', expect='error', code='queue, limit = list(range(10)), 10\nif len(queue) >= limit:\n    raise BufferError("Local: Queue full")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC: callbacks', intro='<p>With Kafka from Lesson 1.5 and <code>pip install confluent-kafka</code>. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Produce with callback', cmd='python l21_send.py', file='terminal', output='produce() o1 returned after 0.96 ms  (in queue: 1)\n…\ncallback  o1 -> partition 2 offset 0  latency 60.0 ms', note='Change the bootstrap address to localhost:9092.'),
           dict(title='2 · Java equivalent', cmd='producer.send(record, (meta, ex) -> System.out.println(meta.offset()));', file='Java', output='0', note='Same model: a Future + callback.')])
TRACE = dict(heading='Queue, then callback', intro='<p>Watch the queue grow and drain.</p>',
    code='queue = []\nqueue.append("o1")\nqueue.append("o2")\nsent = []\nwhile queue:\n    sent.append(queue.pop(0))\nprint(sent, queue)\n',
    notes={3: 'Queued :: produce() returned twice.', 6: 'Sender :: Drains the queue; callbacks fire.'})
WORKED_INTRO = 'Three producer fixes at TiffinGo.'
EXAMPLES = [
    dict(level='b', tag='Producer · shutdown', title='Flush before exit', problem='<p>Orders lost on deploy.</p>', inp='SIGTERM',
         approach=['Catch the stop signal.', 'flush(30).', 'Then exit.'],
         code='import signal\ndef stop(*_):\n    print("flushing...")   # producer.flush(30)\nsignal.signal(signal.SIGTERM, stop)\nprint("handler installed")\n', notes={1: 'Graceful :: No queued record lost.'}, tryit='Scenario 1.'),
    dict(level='i', tag='Producer · errors', title='Count delivery failures', problem='<p>Nobody notices failed sends.</p>', inp='callbacks',
         approach=['Callback increments a metric.', 'Save failed records.', 'Alert on errors.'],
         code='errors = []\ndef cb(err, msg):\n    if err: errors.append(str(err))\ncb("Local: Message timed out", None)\nprint(len(errors), errors)\n', notes={1: 'Visible :: Errors become metrics.'}, tryit='Step 3.'),
    dict(level='a', tag='Producer · back-pressure', title='Handle a full queue', problem='<p>BufferError at peak.</p>', inp='queue limit',
         approach=['Catch BufferError.', 'poll() to drain.', 'Retry produce.'],
         code='attempts = 0\nwhile True:\n    attempts += 1\n    if attempts < 3:\n        continue          # BufferError -> p.poll(0.1)\n    print("produced after", attempts, "attempts"); break\n', notes={1: 'Pacing :: The app slows to Kafka’s speed.'}, tryit='Scenario 2.')]
QUIZ = mix([
    dict(q='Beginner: After produce() returns, the record is…', options=['On disk', 'Queued in the producer', 'Read by consumers', 'Deleted'], answer=1, why='Callback confirms storage.'),
    dict(q='Beginner: What confirms a record was stored?', options=['produce() returning', 'The delivery callback with an offset', 'A log line', 'Nothing'], answer=1, why='Offset = stored.'),
    dict(q='Beginner: Before your program exits, call…', options=['sleep()', 'flush()', 'close the socket', 'nothing'], answer=1, why='Drains the queue.'),
    dict(q='Intermediate: Which component batches records per partition?', options=['Serializer', 'Record accumulator', 'Consumer', 'Controller'], answer=1, why='Then the sender ships them.'),
    dict(q='Intermediate: Unreachable broker with message.timeout.ms=3000 gives…', options=['An exception in produce()', '_MSG_TIMED_OUT in the callback', 'A hang forever', 'Success'], answer=1, why='Step 3.'),
    dict(q='Intermediate: NOT_LEADER_OR_FOLLOWER is…', options=['Non-retriable', 'Retriable: refresh metadata and retry', 'A config error', 'Fatal'], answer=1, why='Leader moved.'),
    dict(q='Advanced: librdkafka raises BufferError when…', options=['The topic is missing', 'The local queue is full', 'acks=0', 'Compression fails'], answer=1, why='Poll and retry.'),
    dict(q='Advanced: The Java producer’s total deadline per record is…', options=['request.timeout.ms', 'delivery.timeout.ms', 'linger.ms', 'max.poll.interval.ms'], answer=1, why='Default 120 s.')])
REVISION = ['produce() = serialise + partition + append to a batch; returns in ~1 ms.', 'Sender thread sends batches to leaders; callback reports offset or error.',
    'Lab: 5 queued, 0 callbacks until flush; 61 ms; median 34 ms, p99 56 ms.', 'Unreachable broker → _MSG_TIMED_OUT after message.timeout.ms (callback only).',
    'Retriable vs non-retriable errors; delivery.timeout.ms 120 s (Java), message.timeout.ms 300 s (librdkafka).', 'Always flush() before exit; poll() regularly; handle BufferError.']
FAQ = [('Is the Java producer thread-safe?', 'Yes. Share one producer per application; creating many producers wastes connections and memory. confluent-kafka Producer is also safe to share between threads.'),
    ('Should I create a producer per request?', 'No. Create it once at startup and reuse it; creation fetches metadata and opens connections.'),
    ('What is the difference between poll() and flush()?', 'poll(t) serves pending callbacks for up to t seconds; flush(t) polls until the queue is empty or t passes.'),
    ('Why are callbacks out of order?', 'They complete per partition batch. Within one partition the order is preserved.'),
    ('Can I send headers?', 'Yes: produce(..., headers=[("source", b"app")]). Headers carry metadata such as trace ids without changing the value.')]
PRACTICE_INTRO = 'Producer programs.'
PROBLEMS = [
    dict(level='easy', title='Queue length', stmt='Count queued records.', inp='3 produces', code='q = []\nfor i in range(3): q.append(i)\nprint(len(q))\n', explain='Like len(producer).'),
    dict(level='easy', title='ms to s', stmt='Convert 300000 ms.', inp='300000', code='print(300000 / 1000, "s")\n', explain='librdkafka message.timeout.ms.'),
    dict(level='easy', title='Error or offset', stmt='Format a delivery report.', inp='err, offset', code='def rep(err, off):\n    return f"error {err}" if err else f"offset {off}"\nprint(rep(None, 7), rep("timeout", None))\n', explain='Callback logic.'),
    dict(level='medium', title='Median', stmt='Median latency.', inp='list', code='import statistics\nprint(statistics.median([30, 34, 35, 60, 56]))\n', explain='35.'),
    dict(level='medium', title='Retry until deadline', stmt='How many retries fit in 120 s with 30 s requests?', inp='120, 30', code='print(120 // 30)\n', explain='About 4 attempts.'),
    dict(level='medium', title='Group callbacks', stmt='Group delivered keys by partition.', inp='pairs', code='from collections import defaultdict\nd = defaultdict(list)\nfor k, p in [("o1", 2), ("o2", 1), ("o3", 2)]: d[p].append(k)\nprint(dict(d))\n', explain='Per-partition order.'),
    dict(level='business', title='Lost revenue', stmt='2,000 lost orders × Rs 300.', inp='numbers', code='print("Rs", 2000 * 300)\n', explain='Why flush matters.'),
    dict(level='business', title='Throughput', stmt='Records/s if each sync send takes 60 ms.', inp='60 ms', code='print(round(1000 / 60), "records/s")\n', explain='Async is far faster.')]
SCN_INTRO = 'Producer questions.'
SCENARIOS = (scn('Any company · backend', 'Fresher', '“Is Kafka send() synchronous?”', 'Explain.', 'answer?', '<p>No. send()/produce() queues the record and returns; a background thread sends batches. You get the result through a callback or Future. flush() waits for all pending records.</p>', '“Yes, it writes to disk.”') +
    scn('Fintech', 'Mid-level', 'Lost events', 'Events vanish during deployments.', 'fix?', '<ul><li>flush()/close() on shutdown.</li><li>Only acknowledge to users after the callback.</li><li>Monitor delivery errors.</li></ul>', 'Blaming Kafka.') +
    scn('Data engineering', 'Mid-level', 'Timeouts', 'Some records fail with timed out during a broker outage.', 'explain?', '<ul><li>They exceeded delivery/message timeout.</li><li>Retriable errors were retried until the deadline.</li><li>Persist failures; tune timeout.</li></ul>', 'Setting retries=0.') +
    scn('Platform', 'Senior', 'Producer design', 'Design the producer layer for 50 services.', 'design?', '<ul><li>One shared, long-lived producer per service.</li><li>Standard config: acks=all, idempotence, linger, compression.</li><li>Metrics: queue, error rate, latency.</li></ul>', 'A producer per request.'))
