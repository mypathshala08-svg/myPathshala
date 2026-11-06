import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from svgkit import scn
BODY = body(HERE)
META = dict(module='11-kafka-in-industry', lesson='02-kafka-vs-rabbitmq-pulsar-and-others', n='11.2', module_label='Module 11 · Kafka in industry',
    title='Kafka vs RabbitMQ, Pulsar and others',
    desc='Kafka compared with RabbitMQ, Apache Pulsar, cloud queues (SQS, Pub/Sub, Service Bus), Kinesis, NATS and Redis Streams: queue vs log, retention and replay, routing, ordering, scaling and operations, with a decision guide. Real lab with RabbitMQ 4.4 and Kafka 4.4: acknowledged messages vanish from a queue, while a Kafka topic serves every group and replays.',
    og_desc='Same five orders into RabbitMQ 4.4 and Kafka 4.4: one forgets, one replays.',
    minutes=20, level='Intermediate',
    lead='When is Kafka the right tool and when is it not? We send the <b>same orders</b> to <b>RabbitMQ</b> and <b>Kafka</b>, add a late consumer, and build a decision guide. <b>All outputs are real.</b>',
    chips=['Queue forgets', 'Log replays', 'Decision guide', 'Runs in your browser (Python)'])
MAIN = '''# Queue (delete on ack) vs log (keep, offsets per group)
orders = ["o1", "o2", "o3", "o4", "o5"]

queue = list(orders)
a, b = queue[0::2], queue[1::2]          # competing consumers
queue.clear()                            # acked -> gone
print("queue: A", a, "B", b, "late reader gets", queue)

log = list(orders)
offsets = {"kitchen": len(log), "billing": len(log)}
late = log[0:]                           # new group starts at 0
print("log: still", len(log), "records; late reader gets", late)
'''
RUN = dict(heading='Run the code: queue vs log', intro='<p>The core difference in plain Python. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('queue.clear()                            # acked -> gone', 'RabbitMQ classic/quorum queues.'), ('late = log[0:]                           # new group starts at 0', 'Kafka replay.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>. Add a third group.', code=None),
        dict(label='2 · Predict first: fan-out', hint='<b>Predict first:</b> 3 groups × 5 orders.', code='print(3 * 5)\n'),
        dict(label='3 · Routing', hint='Topic exchange pattern.', code='import fnmatch\nprint(fnmatch.fnmatch("order.mumbai.veg", "order.*.veg"))\n'),
        dict(label='4 · Priority', hint='Priority queue order.', code='print(sorted([(5, "otp"), (1, "newsletter")], reverse=True))\n'),
        dict(label='5 · Spot the error', hint='RabbitMQ 4 transient queue.', expect='error', code='raise RuntimeError("INTERNAL_ERROR - Feature transient_nonexcl_queues is deprecated")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC: both brokers', intro='<p>Needs Docker. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · RabbitMQ', cmd='docker run -d --name rmq -p 5672:5672 rabbitmq:4-management', file='terminal', output='', note='AMQP on 5672.'),
           dict(title='2 · Run', cmd='pip install pika confluent-kafka && python3 l112.py', file='terminal', output='  late consumer C (billing) gets: nothing, messages are gone after ack', note='Then Kafka part.')])
TRACE = dict(heading='Late reader step by step', intro='<p>Queue vs log.</p>',
    code='queue, log = [], ["o1", "o2"]\nprint("queue:", queue[:1], "log:", log[:1])\n', notes={2: 'Late :: Only the log has data.'})
WORKED_INTRO = 'Three choosing decisions.'
EXAMPLES = [
    dict(level='b', tag='Choose · replay', title='Audit trail', problem='<p>Keep 1 year of events.</p>', inp='need',
         approach=['Replay needed.', 'Long retention.', 'Kafka (+ tiered storage).'], code='print("Kafka")\n', notes={1: 'Log :: Keep.'}, tryit='Guide.'),
    dict(level='i', tag='Choose · routing', title='Route by pattern', problem='<p>Send veg orders in any city to one worker.</p>', inp='need',
         approach=['Topic exchange order.*.veg.', 'RabbitMQ.', 'Or Kafka: separate topics/filters.'], code='print("RabbitMQ topic exchange")\n', notes={1: 'Routing :: Rabbit strength.'}, tryit='Run task 3.'),
    dict(level='a', tag='Choose · combine', title='Both together', problem='<p>Events + tasks.</p>', inp='design',
         approach=['Kafka backbone.', 'Tasks via share groups or RabbitMQ.', 'Bridge with connectors.'], code='print(["Kafka events", "share groups / RabbitMQ tasks"])\n', notes={1: 'Common :: Two tools.'}, tryit='Scenario 2.')]
QUIZ = mix([
    dict(q='Beginner: After ack, RabbitMQ queue messages are…', options=['Kept', 'Deleted', 'Compacted', 'Replicated forever'], answer=1, why='Lab.'),
    dict(q='Beginner: Kafka keeps records until…', options=['Ack', 'Retention/compaction removes them', 'Consumer reads', 'Restart'], answer=1, why='Log.'),
    dict(q='Beginner: Replay is natural in…', options=['RabbitMQ queues', 'Kafka', 'SQS', 'Email'], answer=1, why='Offsets.'),
    dict(q='Intermediate: The late billing consumer in RabbitMQ got…', options=['5 orders', 'Nothing', '3 orders', 'Duplicates'], answer=1, why='Gone.'),
    dict(q='Intermediate: Rich routing (exchanges) is a strength of…', options=['Kafka', 'RabbitMQ', 'Pulsar only', 'None'], answer=1, why='Exchanges.'),
    dict(q='Intermediate: Pulsar stores data in…', options=['ZooKeeper', 'BookKeeper', 'Redis', 'HDFS only'], answer=1, why='Layered.'),
    dict(q='Advanced: Kafka 4.x answer to task queues is…', options=['None', 'Share groups', 'Compaction', 'MM2'], answer=1, why='KIP-932.'),
    dict(q='Advanced: Fair benchmark needs…', options=['Different durability', 'Same durability settings', 'Smallest messages', 'One run'], answer=1, why='Warning.')])
REVISION = ['Queue (ack deletes) vs log (retention, replay, many groups).', 'Lab: RabbitMQ 3+2 split, late reader nothing; Kafka each group 5, replay OK.',
    'RabbitMQ: routing, priorities, RPC; Kafka: event backbone, fan-out, replay.', 'Pulsar: stateless brokers + BookKeeper, multi-tenant; cloud queues: zero ops.', 'Choose by need; often combine.']
FAQ = [('Does RabbitMQ have streams?', 'Yes, RabbitMQ Streams are append-only logs with replay, closer to Kafka for some uses.'),
    ('Is Kafka slower per message?', 'Kafka batches for throughput; with tuning latency is low (ms). RabbitMQ can be lower latency per message at modest rates.'),
    ('What is NATS JetStream?', 'A lightweight messaging system with persistence and replay, popular for edge and microservices.'),
    ('Kinesis vs Kafka?', 'Kinesis is AWS’s managed stream (shards ~ partitions) with different limits and APIs.')]
PRACTICE_INTRO = 'Comparison programs.'
PROBLEMS = [
    dict(level='easy', title='Split', stmt='Round-robin 5 to 2 consumers.', inp='list', code='o = [1, 2, 3, 4, 5]\nprint(o[0::2], o[1::2])\n', explain='3 + 2.'),
    dict(level='easy', title='Fan-out', stmt='4 groups × 100.', inp='ints', code='print(400)\n', explain='Reads.'),
    dict(level='easy', title='Left', stmt='Queue after acks.', inp='list', code='q = [1, 2]\nq.clear()\nprint(q)\n', explain='Empty.'),
    dict(level='medium', title='Pattern', stmt='Match routing key.', inp='str', code='import fnmatch\nprint(fnmatch.fnmatch("order.pune.veg", "order.*.veg"))\n', explain='True.'),
    dict(level='medium', title='Replay from', stmt='Read from offset 2.', inp='list', code='print(["o1", "o2", "o3", "o4"][2:])\n', explain='o3, o4.'),
    dict(level='medium', title='Pick', stmt='Rules engine.', inp='dict', code='need = {"replay": True, "routing": False}\nprint("Kafka" if need["replay"] else "RabbitMQ")\n', explain='Kafka.'),
    dict(level='business', title='Systems', stmt='Run both or one?', inp='ints', code='print("one if share groups fit")\n', explain='Simplify.'),
    dict(level='business', title='Retention cost', stmt='1 TB/day × 30 days.', inp='ints', code='print(30, "TB")\n', explain='Plan storage.')]
SCN_INTRO = 'Comparison interview questions.'
SCENARIOS = (scn('Any company · data', 'Fresher', '“Kafka vs RabbitMQ?”', 'Explain.', 'answer?', '<p>RabbitMQ is a message broker: routes messages to queues and deletes them after ack; great for tasks and routing. Kafka is a distributed log: keeps data, many groups read independently and can replay; great for event streaming.</p>', '“Kafka is just faster.”') +
    scn('Startup', 'Mid-level', 'Choose for tasks', 'Background jobs only.', 'pick?', '<ul><li>RabbitMQ/SQS, or share groups if on Kafka.</li></ul>', 'Kafka with 1 partition.') +
    scn('E-commerce', 'Mid-level', 'Need history', 'New team wants past events.', 'pick?', '<ul><li>Kafka with retention; replay.</li></ul>', 'RabbitMQ queue.') +
    scn('Architecture', 'Senior', 'Pulsar?', 'Multi-tenant SaaS.', 'consider?', '<ul><li>Tenancy, geo, tiered storage, ops, ecosystem.</li></ul>', 'Choose by hype.'))
