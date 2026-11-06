import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from kafkakit import *
C = 'l101_monitor.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('Your consumer says it has received all 30,000 orders, yet the dashboard says it is 9,000 behind. Which one is lying?',
    'Neither. <b>Consumer lag</b> is measured from <b>committed offsets</b>, while the client had already <b>prefetched</b> everything into memory. In our lab we produced 30,000 orders, ran a slow consumer, watched lag fall from 9,626 to 8,980, read broker health over <b>JMX</b>, paused a broker and saw <code>UnderReplicatedPartitions</code> jump from 0 to 3 and back.',
    ['The handful of metrics that tell you a cluster is healthy.',
     'Consumer lag: how it is computed and why it can mislead.',
     'JMX, client stats, CLI tools and what to alert on.'])
cmap = concept_map('Concept map. Beginner: lag, offsets, broker metrics. Intermediate: JMX, under-replicated partitions, request idle %, client stats. Advanced: lag in time, alert design, exporters and dashboards, controller metrics.',
    [[('of', 'Offsets + commits', 'Lesson 3.3', B + '03-consumers/03-offsets-commits-and-lag/'), ('ur', 'ISR + URP', 'Lesson 5.2', B + '05-replication-and-the-cluster/02-isr-and-the-high-watermark/')],
     [('lg', 'Consumer lag', 'end − committed', None), ('jm', 'JMX metrics', 'broker MBeans', None), ('cs', 'Client stats', 'producer/consumer', None), ('ld', 'Disk usage', 'kafka-log-dirs', None)],
     [('lt', 'Lag in time', 'seconds behind', None), ('al', 'Alert design', 'what pages you', None), ('ex', 'Exporters + dashboards', 'Prometheus/Grafana', None), ('tn', 'Tuning', 'Lesson 10.2', B + '10-kafka-in-production/02-performance-tuning-and-partition-sizing/')]],
    [('of', 'lg'), ('ur', 'jm'), ('lg', 'lt'), ('jm', 'al'), ('cs', 'lg'), ('jm', 'ex'), ('ld', 'al'), ('al', 'tn')],
    {'lg', 'jm', 'cs', 'ld', 'lt', 'al', 'ex'},
    '<b>Builds on:</b> <a href="../../03-consumers/03-offsets-commits-and-lag/">3.3</a>, <a href="../../05-replication-and-the-cluster/02-isr-and-the-high-watermark/">5.2</a>. <b>Next:</b> <a href="../02-performance-tuning-and-partition-sizing/">10.2 Tuning</a>.')
whw = why_how_where(
    'Kafka rarely fails loudly. A slow consumer, a lagging follower or a full disk shows up first as a number drifting. Watching the right numbers turns 2 a.m. outages into daytime tickets.',
    'Brokers expose metrics as JMX MBeans (e.g. <code>kafka.server:type=ReplicaManager,name=UnderReplicatedPartitions</code>); clients expose their own metrics; lag = log-end offset − committed offset per partition, from <code>kafka-consumer-groups</code> or the Admin API. An exporter scrapes them into Prometheus/Grafana or your vendor’s monitoring.',
    'Every production cluster: on-call dashboards, SLOs for “orders processed within 1 minute”, capacity planning, and incident diagnosis.',
    'Too many metrics hide the important ones. Lag in messages means little without throughput: 10,000 behind at 10,000/s is 1 s; at 50/s it is over 3 minutes.')

def dash(urp=0, hl=-1):
    tiles = [('URP', str(urp), 'red' if urp else 'green'), ('Offline', '0', 'green'), ('Controllers', '1', 'green'), ('Lag', '8,980', 'amber')]
    o = ''
    for k, (n, v, tn) in enumerate(tiles):
        o += box(8 + k * 88, 34, 80, 64, 'acc' if k == hl else tn, rx=8) + t(48 + k * 88, 56, n, 7.8, bold=True) + t(48 + k * 88, 82, v, 13, bold=True)
    return o + t(180, 20, 'on-call dashboard: four numbers first', 7.6)
scene_svg = scene('An on-call dashboard with four tiles: under-replicated partitions 0, offline partitions 0, active controllers 1, consumer lag 8,980.', dash(),
                  'Four numbers answer “is Kafka OK?”: <tspan font-weight="700" class="s-acc">URP, offline, controller, lag</tspan>.')
dialogue = '''K> Sir, the kitchen dashboard shows 9,000 orders lag but the consumer log says it received all 30,000. Is the lag tool broken?
A> No. The client <b>prefetched</b> records, but lag counts what the group has <b>committed</b>. Received is not processed.
R> And how do we know the brokers themselves are fine?
A> JMX. A few broker metrics say almost everything. Let’s read them, then break a broker on purpose.'''

lv = '''
LEVELS> Monitoring at three levels
L1> A hospital ward
      <ul>
        <li>Nurses don’t read every chart; they watch pulse, oxygen and temperature. For Kafka: under-replicated partitions, offline partitions, one active controller, and consumer lag.</li>
      </ul>
L2> The core metrics
      <ul>
        <li><b>Cluster</b>: UnderReplicatedPartitions (should be 0), OfflinePartitionsCount (0), ActiveControllerCount (exactly 1 across the cluster), UncleanLeaderElectionsPerSec (0), under-min-ISR partitions.</li>
        <li><b>Load</b>: MessagesInPerSec, BytesIn/OutPerSec, RequestHandlerAvgIdlePercent and NetworkProcessorAvgIdlePercent (alert when below ~0.3), request latencies (Produce/Fetch TotalTimeMs p99).</li>
        <li><b>Consumers</b>: lag per group and partition (end − committed), plus <code>records-lag-max</code> in the client; better, lag converted to seconds.</li>
      </ul>
L3> Doing it well
      <ul>
        <li>Collect with a JMX exporter (Prometheus) or vendor agent; Kafka 4.x also supports client telemetry push (KIP-714) to the broker.</li>
        <li>Alert on symptoms users feel (lag in seconds, URP for > 5 min, offline > 0), not on every metric. Add disk usage and growth (kafka-log-dirs), and ISR shrink/expand rates.</li>
        <li>Lag tools (Burrow, Kafka Lag Exporter, vendor UIs) evaluate trends: lag rising while the consumer is “up” means it is too slow or stuck.</li>
      </ul>
/LEVELS
'''
DIS = figure('Dissection of one JMX metric name: domain kafka.server, type ReplicaManager, name UnderReplicatedPartitions, attribute Value, read with JmxTool from broker 1 on port 9101.',
    t(16, 22, 'One JMX metric (real, broker 1)', 8.6, 'ink', anchor='start', bold=True) +
    fields(16, 34, [('kafka.server', 'blue', 1), (':type=ReplicaManager', 'violet', 2), (',name=UnderReplicatedPartitions', 'amber', 3), ('Value = 0', 'green', 4)]) +
    legend(16, 84, [(1, 'Domain', 'kafka.server, kafka.controller, kafka.network …'), (2, 'Type', 'the component'), (3, 'Name', 'the metric'),
                    (4, 'Attribute', 'Value for gauges; Count / OneMinuteRate / 99thPercentile for meters and timers')], size=8, gap=15, w=90),
    h=158, caption='JMX is enabled with JMX_PORT (we used 9101).')
extra = '''

  <h3>Dissect a metric name</h3>
''' + DIS

types_html = table(['Metric', 'Healthy', 'Alert when', 'Our lab'], [
    ['UnderReplicatedPartitions', '0', '> 0 for minutes', '0 → 3 (k3 paused) → 0'], ['OfflinePartitionsCount', '0', '> 0 (page!)', '0'],
    ['ActiveControllerCount (sum)', '1', '≠ 1', '0 on broker 1 (leader is 2)'], ['RequestHandlerAvgIdlePercent', '> 0.3', '< 0.2', '0.99'],
    ['Produce TotalTimeMs p99', 'low, stable', 'rising', '24 ms'], ['Consumer lag (s)', 'near 0', '> SLO', '~9,000 msgs'],
], minw=640) + table(['Tool', 'Shows'], [
    ['kafka-consumer-groups --describe', 'lag per partition'], ['JmxTool / JMX exporter', 'broker metrics'], ['client stats (stats_cb, metrics())', 'client view'],
    ['kafka-log-dirs --describe', 'disk per partition'], ['kafka-metadata-quorum describe', 'controller health'],
], minw=520)
warn = 'Do not alert on raw lag numbers alone. Convert lag to time (lag ÷ consume rate) and alert when it exceeds what the business accepts, and when lag grows steadily for several minutes. And note: kafka-consumer-groups shows a partition with no committed offset as "-", not 0.'

steps = [
    ('Step 1 · Load',
     code('bash', 'terminal', 'kafka-producer-perf-test.sh --topic orders-101 --num-records 30000 --record-size 200 --throughput 2000 --command-property bootstrap.servers=k1:9092', sec('== 1)', '== 2)')),
     '30,000 orders at about 2,000/s. p99 latency 229 ms.'),
    ('Step 2 · A slow consumer and its lag',
     code('python', 'slow.py', "c = Consumer({..., 'group.id': 'slow-kitchen-101', 'statistics.interval.ms': 2000, 'stats_cb': stats})\nwhile ...: m = c.poll(0.1); time.sleep(0.02)   # ~50 orders/s", sec('== 2)', '== 3)')),
     'Lag on p2 fell slowly: 9,626 → 9,129 → 8,980. p0 and p1 show "-": nothing committed yet. The client stats say rx msgs 30,000: librdkafka had prefetched everything, but only 733 were processed and committed. Lag = what is not committed.'),
    ('Step 3 · Broker health over JMX',
     code('bash', 'terminal', 'docker run … -e JMX_PORT=9101 apache/kafka:4.4.0\nkafka-run-class.sh org.apache.kafka.tools.JmxTool --jmx-url service:jmx:rmi:///jndi/rmi://k1:9101/jmxrmi \\\n  --object-name kafka.server:type=ReplicaManager,name=UnderReplicatedPartitions --one-time true', sec('== 3)', '== 4)')),
     'All healthy: no URP, no offline partitions, request handlers 99% idle. ActiveControllerCount 0 on broker 1 is correct: the active controller is node 2 (Lesson 5.4); the sum across nodes must be 1.'),
    ('Step 4 · Break it',
     code('bash', 'terminal', 'docker pause k3; sleep 14   # then read URP; docker unpause k3', sec('== 4)', '== 5)')),
     'URP went to 3 and back to 0. IsrShrinksPerSec stayed 0 on broker 1: k3 left the ISR by controller fencing (Lesson 5.2), not by a leader-driven shrink, so watch URP, not only shrink rates.'),
    ('Step 5 · Disk',
     code('bash', 'terminal', 'kafka-log-dirs.sh --bootstrap-server k1:9092 --describe --topic-list orders-101', sec('== 5)')),
     '6.4 MB of 200-byte orders on each broker (RF 3 = three equal copies).'),
]
see = [term([('30000 records', W), ('p99 229 ms', Y)], size=7.2), term([('p2 lag 9626 → 8980', Y), ('p0,p1 "-"', W), ('rx msgs 30000', RD)], size=7.0),
       term([('URP 0 · offline 0', G), ('idle 0.99 · p99 24 ms', G)], size=7.0), term([('k3 paused: URP 3', RD), ('back: URP 0', G)], size=7.2),
       term([('6.40 MB x 3 brokers', W)], size=7.2)]
B1 = [dash(0, 3), dash(0, 3), dash(0, 0), dash(3, 0), dash(0, -1)]
B1 = [b + cap(c, '', tn, y=118, h=30) for b, c, tn in zip(B1, ['Load arrives', 'Lag = not committed', 'All green', 'URP alarm', 'Disk checked'], ['blue', 'amber', 'green', 'red', 'blue'])]
two = anim_two('Monitoring', 'Lag, JMX, alarm', 'Real outputs from the lab', 'The dashboard', see, B1, ['Load.', 'Lag.', 'JMX.', 'Break.', 'Disk.'], ['Produce.', 'Committed.', 'Healthy.', 'Alert.', 'Size.'])
pe = peel('A lag number, layer by layer', 'p2 lag 8,980. (From the lab.)',
    [('Log end', ''), ('Committed', ''), ('Subtract', ''), ('Rate', ''), ('Time', ''), ('Decide', '')],
    [['Log end', 'p2 end offset', '9,713', ''], ['Committed', '__consumer_offsets', '733', ''], ['Subtract', '9,713 − 733', '= 8,980', ''],
     ['Rate', 'consumer ~50/s', '', ''], ['Time', '8,980 ÷ 50', '≈ 180 s behind', ''], ['Decide', 'SLO 60 s?', '→ alert, scale out', '']],
    ['End.', 'Commit.', 'Lag.', 'Rate.', 'Seconds.', 'Act.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'Lag climbs every lunch', 'Kitchen consumer too slow. (Typical.)', ('Lag in time', 'Measure, then scale'), [
    ('Lag 50k at 12:30', 'rising', 'Alert.', 'red'), ('Lag ÷ rate', '≈ 8 minutes', 'Meaningful.', 'amber'),
    ('Add consumers', 'up to partitions', 'Scale.', 'green'), ('Or speed up processing', 'batch DB writes', 'Fix.', 'green'),
    ('Lag back to seconds', 'dashboard green', 'Done.', 'blue')], ['Climb.', 'Measure.', 'Scale.', 'Optimise.', 'Green.'], 'scenario-lag') + \
       five('Real-time scenario 2', 'URP for an hour', 'One broker slow. (Typical.)', ('UnderReplicatedPartitions', 'Find the slow broker'), [
    ('URP 120', 'all with follower 4', 'Pattern.', 'red'), ('Broker 4 disk 100% util', 'iostat', 'Cause.', 'amber'),
    ('Replace disk / move load', 'reassign', 'Fix.', 'green'), ('URP 0', 'ISR full', 'Healthy.', 'green'),
    ('Alert on URP > 5 min', 'not instant', 'Tune.', 'blue')], ['URP.', 'Disk.', 'Fix.', 'Zero.', 'Alert.'], 'scenario-urp') + \
       five('Real-time scenario 3 · advanced', 'Lag 0 but nothing processed', 'Stuck consumer. (Typical.)', ('Trend + liveness', 'Lag alone can lie'), [
    ('No new input', 'lag 0', 'Looks fine.', 'amber'), ('Consumer hung on DB', 'no commits', 'Hidden.', 'red'),
    ('Input resumes', 'lag grows, no commits', 'Detect.', 'amber'), ('Alert: committed offset not moving', 'while end moves', 'Signal.', 'green'),
    ('Add processing heartbeat metric', 'per app', 'Robust.', 'blue')], ['Quiet.', 'Hung.', 'Grow.', 'Detect.', 'Heartbeat.'], 'scenario-stuck')
assemble(HERE, h2_story='Is Kafka OK right now?', hook_html=hk,
    narration='TiffinGo’s on-call engineer needs one screen that answers “is Kafka healthy and are orders being processed in time?”. Kabir has to choose the numbers.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Monitoring and consumer lag',
    formal='<b>Kafka monitoring</b> collects broker, controller and client metrics (exposed through JMX MBeans and client metric APIs) to track availability, throughput, latency and resource use. <b>Consumer lag</b> for a group and partition is the difference between the partition’s log-end offset and the group’s committed offset; it measures unprocessed (uncommitted) data, not data fetched by the client.',
    simple='Watch a few numbers: copies missing (URP), partitions with no leader (offline), exactly one controller, and how far each consumer group is behind (lag). Lag counts what has not been committed yet.',
    term_rows=[('Lag', 'End offset − committed offset.'), ('URP', 'Partitions missing ISR copies.'), ('Offline partition', 'No leader.'), ('JMX', 'Java metrics interface.'), ('MBean', 'One metric object.'), ('Idle percent', 'Spare broker threads.'), ('Exporter', 'Sends metrics to Prometheus.'), ('Lag in time', 'Lag ÷ consume rate.')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('Received means processed.', 'Lag counts committed offsets; clients prefetch.', 'Step 2: rx 30,000, committed 733.'),
               ('Every broker should report ActiveControllerCount 1.', 'Only the active one; the sum is 1.', 'Step 3.'),
               ('ISR shrink metrics catch every lost replica.', 'Fencing removes replicas too; watch URP.', 'Step 4.')],
    exam='“How do you monitor Kafka?” Broker JMX: URP, offline partitions, active controller, request idle %, latencies, bytes in/out; consumer lag = end − committed per partition, convert to time; disk usage; exporters + alerts on symptoms.',
    types_h2='What to watch', types_html=types_html, warn=warn,
    steps_h2='Measure, then break', steps_intro='All outputs are real: Kafka 4.4.0, 3 brokers, broker 1 restarted with JMX_PORT=9101.',
    steps=steps, two=two, peel_intro='Now peel one lag number.', peel_html=pe,
    scen_intro='Three live scenarios: lunch lag, a slow broker, and a stuck consumer.', scen=scen,
    uc_h2='Monitoring at work', ucs=[uc_('oncall', 'on-call', 'red', '1. On-call dashboards', 'Four numbers, clear alerts.', ['Metrics', '*rules', 'Pager']),
        uc_('slo', 'SLO', 'blue', '2. Processing SLOs', 'Lag in seconds per group.', ['Lag', '*÷ rate', 'SLO']),
        uc_('cap', 'capacity', 'green', '3. Capacity planning', 'Bytes in/out, disk growth.', ['Trends', '*forecast', 'Brokers']),
        uc_('diag', 'diagnose', 'violet', '4. Incident diagnosis', 'Which broker, which partition.', ['Alert', '*drill down', 'Cause'])],
    uc_note='Examples are simplified descriptions of common practice.',
    pre='<b>Before you start:</b> <a href="../../03-consumers/03-offsets-commits-and-lag/">3.3 Lag</a>.')
