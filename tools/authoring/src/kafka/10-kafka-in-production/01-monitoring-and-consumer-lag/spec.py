import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from svgkit import scn
BODY = body(HERE)
META = dict(module='10-kafka-in-production', lesson='01-monitoring-and-consumer-lag', n='10.1', module_label='Module 10 · Kafka in production',
    title='Monitoring and consumer lag',
    desc='How to monitor Kafka in production: consumer lag (end minus committed offset) and lag in time, prefetching vs processing, broker JMX metrics (UnderReplicatedPartitions, OfflinePartitionsCount, ActiveControllerCount, idle percentages, request latencies), client statistics, disk usage and alert design. Real Kafka 4.4 lab with JMX: lag falling under a slow consumer, and URP jumping to 3 when a broker is paused.',
    og_desc='Lag 9,626 → 8,980, URP 0 → 3 → 0: monitoring Kafka 4.4 with JMX and consumer lag.',
    minutes=22, level='Intermediate',
    lead='How do you know Kafka is healthy and consumers keep up? We measure <b>lag</b>, read broker <b>JMX</b> metrics, and break a broker to see the <b>alarm</b>. <b>All outputs are real.</b>',
    chips=['Lag from commits', 'URP 0 → 3 → 0', 'JMX on :9101', 'Runs in your browser (Python)'])
MAIN = '''# Consumer lag per partition, and lag in time
end       = {0: 10447, 1: 9840, 2: 9713}
committed = {0: None,  1: None, 2: 733}
rate = 50                                  # records/s the group processes

for p in end:
    if committed[p] is None:
        print(f"p{p}: no committed offset yet ('-')")
        continue
    lag = end[p] - committed[p]
    print(f"p{p}: lag {lag} records = {lag / rate / 60:.1f} minutes behind")
'''
RUN = dict(heading='Run the code: lag', intro='<p>Lag the way the tools compute it. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('    lag = end[p] - committed[p]', 'Lag = log end − committed.'), ('    print(f"p{p}: lag {lag} records = {lag / rate / 60:.1f} minutes behind")', 'Convert to time for alerts.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>. Set rate = 500.', code=None),
        dict(label='2 · Predict first: controllers', hint='<b>Predict first:</b> sum of ActiveControllerCount over 3 nodes.', code='print(0 + 1 + 0)\n'),
        dict(label='3 · Idle alarm', hint='Alert if idle < 0.3.', code='idle = 0.99\nprint("ALERT" if idle < 0.3 else "ok")\n'),
        dict(label='4 · URP rule', hint='Alert only if URP > 0 for 5 checks.', code='urp = [0, 3, 3, 3, 3, 3]\nprint(all(u > 0 for u in urp[-5:]))\n'),
        dict(label='5 · Spot the error', hint='JMX port clash.', expect='error', code='raise OSError("Port already in use: 9101 (JMX_PORT is set for every Kafka tool in the container; unset it for CLI tools)")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC: watch the cluster', intro='<p>Needs the lab; broker started with JMX_PORT. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Lag', cmd='kafka-consumer-groups.sh --bootstrap-server k1:9092 --describe --group slow-kitchen-101', file='terminal', output='orders-101 2 733 9713 8980', note='current, end, lag.'),
           dict(title='2 · JMX', cmd='docker exec -e JMX_PORT= k1 kafka-run-class.sh org.apache.kafka.tools.JmxTool --jmx-url service:jmx:rmi:///jndi/rmi://k1:9101/jmxrmi --object-name kafka.server:type=ReplicaManager,name=UnderReplicatedPartitions --one-time true', file='terminal', output='"time","…UnderReplicatedPartitions:Value"\n1793946528828,0', note='Healthy.'),
           dict(title='3 · Disk', cmd='kafka-log-dirs.sh --bootstrap-server k1:9092 --describe --topic-list orders-101', file='terminal', output='', note='JSON per broker.')])
TRACE = dict(heading='Lag step by step', intro='<p>End, committed, time.</p>',
    code='end, committed, rate = 9713, 733, 50\nlag = end - committed\nseconds = lag / rate\nprint(lag, round(seconds))\n',
    notes={2: 'Lag :: 8,980 records.', 3: 'Time :: ~180 s behind.'})
WORKED_INTRO = 'Three monitoring decisions.'
EXAMPLES = [
    dict(level='b', tag='Monitor · first', title='First dashboard', problem='<p>Four tiles only.</p>', inp='metrics',
         approach=['URP.', 'Offline partitions.', 'Active controller.', 'Lag per group.'], code='print(["URP", "Offline", "ActiveController", "Lag"])\n', notes={1: 'Focus :: Symptoms first.'}, tryit='Scene.'),
    dict(level='i', tag='Monitor · lag', title='Lag alert', problem='<p>Orders must be cooked within 2 min.</p>', inp='SLO',
         approach=['lag ÷ rate.', 'Alert > 120 s for 5 min.', 'Also alert on non-moving commits.'], code='print("alert if lag_seconds > 120 for 5m")\n', notes={1: 'Time :: Business meaning.'}, tryit='Peel.'),
    dict(level='a', tag='Monitor · stack', title='Collect metrics', problem='<p>Self-managed cluster.</p>', inp='stack',
         approach=['JMX exporter on brokers.', 'Prometheus + Grafana.', 'Lag exporter.'], code='print("jmx_exporter -> Prometheus -> Grafana + alerts")\n', notes={1: 'Standard :: Open source.'}, tryit='Types table.')]
QUIZ = mix([
    dict(q='Beginner: Consumer lag is…', options=['Network delay', 'End offset − committed offset', 'Broker CPU', 'Topic size'], answer=1, why='Per partition.'),
    dict(q='Beginner: UnderReplicatedPartitions healthy value…', options=['1', '0', '3', 'any'], answer=1, why='All copies in sync.'),
    dict(q='Beginner: Broker metrics are exposed via…', options=['SQL', 'JMX', 'ZooKeeper', 'Email'], answer=1, why='MBeans.'),
    dict(q='Intermediate: rx msgs 30,000 but lag 8,980 means…', options=['Tool bug', 'Prefetched but not processed/committed', 'Data loss', 'Duplicates'], answer=1, why='Step 2.'),
    dict(q='Intermediate: When k3 was paused URP became…', options=['0', '3', '30', '−1'], answer=1, why='Step 4.'),
    dict(q='Intermediate: ActiveControllerCount 0 on broker 1 means…', options=['Cluster down', 'Another node is the active controller', 'Bug', 'No metadata'], answer=1, why='Sum = 1.'),
    dict(q='Advanced: Best lag alert is based on…', options=['Raw records', 'Lag in time vs SLO', 'Disk size', 'Partitions'], answer=1, why='Meaning.'),
    dict(q='Advanced: "-" in CURRENT-OFFSET means…', options=['Lag 0', 'No committed offset', 'Partition offline', 'Compacted'], answer=1, why='Step 2.')])
REVISION = ['Lag = end − committed; prefetched ≠ processed.', 'Core broker metrics: URP, offline, active controller (sum 1), idle %, p99 latencies.',
    'Lab: lag 9,626 → 8,980; URP 0 → 3 → 0 with k3 paused; 6.4 MB per broker.', 'Alert on lag in time and stuck commits, URP for minutes, offline > 0.', 'JMX exporter → Prometheus/Grafana; KIP-714 client metrics.']
FAQ = [('How do I enable JMX?', 'Set JMX_PORT (and KAFKA_JMX_OPTS) for the broker process; unset it for CLI tools in the same container.'),
    ('What about consumers that commit rarely?', 'Lag looks high between commits; use processing metrics too.'),
    ('Which tools show lag?', 'kafka-consumer-groups, Admin API, Burrow, Kafka Lag Exporter, vendor consoles.'),
    ('Share groups lag?', 'Kafka 4.2 added share-partition lag metrics (KIP-1226).')]
PRACTICE_INTRO = 'Monitoring programs.'
PROBLEMS = [
    dict(level='easy', title='Lag', stmt='End 500, committed 450.', inp='ints', code='print(500 - 450)\n', explain='50.'),
    dict(level='easy', title='Seconds', stmt='Lag 6000 at 200/s.', inp='ints', code='print(6000 / 200)\n', explain='30 s.'),
    dict(level='easy', title='Controllers', stmt='Healthy sum?', inp='list', code='print(sum([0, 1, 0]) == 1)\n', explain='True.'),
    dict(level='medium', title='Total lag', stmt='Sum partitions, skip None.', inp='dict', code='lags = {0: None, 1: 20, 2: 8980}\nprint(sum(v for v in lags.values() if v is not None))\n', explain='9000.'),
    dict(level='medium', title='Stuck', stmt='Committed not moving, end moving.', inp='lists', code='c, e = [733, 733, 733], [9713, 9800, 9900]\nprint(len(set(c)) == 1 and e[-1] > e[0])\n', explain='Stuck.'),
    dict(level='medium', title='Disk growth', stmt='6.4 MB per 30k msgs; 10M msgs?', inp='ints', code='print(round(6.4 / 30000 * 10_000_000 / 1024, 1), "GB per broker")\n', explain='~2.1 GB.'),
    dict(level='business', title='SLO', stmt='Lag 9000 at 50/s vs 120 s SLO.', inp='ints', code='print(9000 / 50 > 120)\n', explain='Breach.'),
    dict(level='business', title='Consumers needed', stmt='Need 300/s, each 50/s.', inp='ints', code='print(300 // 50)\n', explain='6 (≤ partitions).')]
SCN_INTRO = 'Monitoring interview questions.'
SCENARIOS = (scn('Any company · data', 'Fresher', '“What is consumer lag?”', 'Explain.', 'answer?', '<p>For each partition, how many records exist after the group’s committed offset (log end − committed). Rising lag means consumers are slower than producers.</p>', '“Network latency.”') +
    scn('Platform', 'Mid-level', 'Which metrics?', 'Design alerts.', 'answer?', '<ul><li>URP, offline, controller count, idle %, p99 latency.</li><li>Lag in time per group.</li></ul>', 'Alert on everything.') +
    scn('Platform', 'Mid-level', 'URP not clearing', 'For an hour.', 'do?', '<ul><li>Find the common follower.</li><li>Check its disk, GC, network.</li></ul>', 'Restart all brokers.') +
    scn('Data', 'Senior', 'Lag 0, no output', 'Business sees nothing.', 'why?', '<ul><li>No input, or stuck consumer.</li><li>Monitor commits moving and app heartbeats.</li></ul>', 'Trust lag alone.'))
