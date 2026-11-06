import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from kafkakit import *
S, P = 'l16_setup.txt', 'l16_projects.txt'
def sec(c, a, b=None, drop=()):
    return capsec(c, a, b, drop)
JOBS = os.path.join(HERE, '..', '..', 'lab', 'jobs', 'projects')
def src(n):
    return open(os.path.join(JOBS, n)).read().strip()
B = '../../'
HOOK = hook('Can you build a real-time fraud alert system in one evening?',
    'Yes: two small Python programs and one Kafka topic in between. In this lesson you build <b>two real-time projects</b> end to end, on a Linux VM or in free Google Colab, and every output shown was produced by running exactly these steps.',
    ['A live dashboard that updates revenue per city while orders stream in.',
     'A 3-stage pipeline: payments → fraud detector → alerts topic → SMS notifier.',
     'Why the notifier never needs to know the detector exists.'])
MAP = concept_map('Concept map. Beginner: install Kafka from the binary, create topics, run a producer and a consumer. Intermediate: consumer groups and lag, keys and partitions, stateful logic in a consumer. Advanced: chaining topics into pipelines, Kafka Streams, exactly-once.',
    [[('in', 'Install from binary', 'VM or Colab', None), ('tp', 'Create topics', 'kafka-topics.sh', B + '01-introduction/05-install-kafka-and-cli-tools/'), ('pc', 'Producer + consumer', 'confluent-kafka', None)],
     [('gr', 'Groups + lag', 'Lesson 3.3', B + '03-consumers/03-offsets-commits-and-lag/'), ('ky', 'Keys → partitions', 'Lesson 1.4', B + '01-introduction/04-topics-partitions-and-offsets/'), ('st', 'State in a consumer', 'sliding window', None)],
     [('pl', 'Topic → topic pipelines', 'this lesson', None), ('ks', 'Kafka Streams', 'Lesson 9.1', B + '09-stream-processing/01-kafka-streams/'), ('eo', 'Exactly-once', 'Lesson 3.5', B + '03-consumers/05-transactions-and-exactly-once/')]],
    [('in', 'gr'), ('tp', 'ky'), ('pc', 'st'), ('st', 'pl'), ('pl', 'ks'), ('gr', 'eo')],
    {'in', 'pc', 'st', 'pl'},
    '<b>Builds on:</b> 1.1–1.5. <b>Next:</b> Module 2 explains every producer setting used here.')
WHW = why_how_where(
    'Reading about Kafka is not the same as building with it. Two complete projects make every concept of Module 1 concrete.',
    'Kafka runs as one KRaft node; Python producers write JSON events with keys; consumers in groups compute results and can write to new topics.',
    'Live order dashboards, payment fraud checks, IoT alerts, delivery tracking.',
    'Colab sessions are temporary; production needs a multi-broker cluster, monitoring and security (Module 10).')

def p1_svg():
    o = t(320, 18, 'Project 1 · TiffinGo live order tracker', 9.6, bold=True)
    o += box(14, 40, 140, 64, 'card', rx=8) + icon('cart', 24, 50, 1.1) + t(60, 62, 'p1_order_producer', 7.6, 'ink', anchor='start', bold=True, mono=True) + t(60, 76, '1 order / 0.2 s', 7.4, 'ink2', anchor='start') + t(60, 90, 'key = city', 7.4, 'ink2', anchor='start')
    o += arrow(154, 72, 200, 72, 'acc', 1.6)
    o += box(200, 32, 220, 84, 'blue', rx=10) + t(310, 48, 'topic orders (3 partitions)', 8.4, bold=True)
    o += pcol(236, 56, 'P0', ['Pune', 'Delhi'], 'card', cw=40, ch=14) + pcol(236, 74, 'P1', ['Mum', 'Blr'], 'card', cw=40, ch=14) + pcol(236, 92, 'P2', [], 'card', cw=40, ch=14) + t(290, 102, '(empty: 4 keys)', 7, 'red', anchor='start')
    o += arrow(420, 72, 466, 72, 'green', 1.6)
    o += box(466, 40, 160, 64, 'card', rx=8) + icon('chart', 476, 50, 1.1) + t(510, 62, 'p1_live_dashboard', 7.6, 'ink', anchor='start', bold=True, mono=True) + t(510, 76, 'revenue per city', 7.4, 'ink2', anchor='start') + t(510, 90, 'alert if ≥ Rs 1,000', 7.4, 'ink2', anchor='start')
    o += t(546, 124, 'group: live-dashboard', 7.4, 'green', mono=True)
    return figure('Project 1: a producer sends one order every 0.2 seconds keyed by city into topic orders with three partitions; the live dashboard consumer in group live-dashboard keeps revenue per city and raises an alert for orders of 1,000 rupees or more.', o, h=150)
def p2_svg():
    o = t(320, 18, 'Project 2 · UPI fraud alert pipeline', 9.6, bold=True)
    stages = [('card', 'payments\nproducer', 'card'), (None, 'payments', 'blue'), ('gear', 'fraud\ndetector', 'card'), (None, 'fraud-alerts', 'red'), ('sms', 'sms\nnotifier', 'card')]
    for k, (ic, nm, tone) in enumerate(stages):
        x = 14 + k * 126
        if ic:
            o += box(x, 40, 110, 64, tone, rx=8) + icon(ic, x + 8, 48, 1.0) + ''.join(t(x + 38, 62 + j * 13, ln, 7.8, 'ink', anchor='start', bold=True) for j, ln in enumerate(nm.split('\n')))
        else:
            o += cyl(x + 10, 40, 90, 64, nm, tone, size=7.6)
        if k < 4:
            o += arrow(x + 110, 72, x + 126, 72, 'acc', 1.6)
    o += t(321, 122, 'group: fraud-detector', 7.2, 'green', mono=True) + t(573, 122, 'group: sms-notifier', 7.2, 'green', mono=True)
    o += t(321, 136, 'rules: > Rs 50,000 · > 4 payments in 60 s', 7.2, 'ink2')
    return figure('Project 2: a payments producer writes to topic payments; the fraud detector consumer applies two rules and writes alerts to topic fraud-alerts; a separate SMS notifier consumer reads the alerts.', o, h=156)

sc_ = (box(14, 22, 296, 108, 'card', rx=10) + t(162, 40, 'Option A · Linux VM', 9, bold=True) + icon('disk', 28, 52, 1.0) +
       ''.join(t(62, 62 + k * 14, s, 7.6, 'ink2', anchor='start', mono=True) for k, s in enumerate(['sudo apt install openjdk-21-jre-headless', 'wget kafka_2.13-4.4.0.tgz && tar -xzf', 'kafka-storage.sh format --standalone', 'kafka-server-start.sh (background)'])) +
       box(330, 22, 296, 108, 'card', rx=10) + t(478, 40, 'Option B · Google Colab', 9, bold=True) + icon('chart', 344, 52, 1.0) +
       ''.join(t(378, 62 + k * 14, s, 7.6, 'ink2', anchor='start', mono=True) for k, s in enumerate(['open our notebook (.ipynb)', 'Runtime → Run all', 'Kafka + both projects', 'free, nothing to install'])))
scene_svg = scene('Two ways to run the projects: a Linux virtual machine with Java and the Kafka binary, or a Google Colab notebook that installs and runs everything.', sc_,
                  'Same Kafka, same code: <tspan font-weight="700" class="s-acc">VM or Colab</tspan>.')
story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>From theory to two running systems</h2>
  <div class="story">
{HOOK}
    <p class="narration">Module 1 is done. Riya’s college laptop cannot run Docker, and Kabir only has a cloud VM. Arjun Sir gives them one evening to build something real.</p>

{scene_svg}

R> Sir, without Docker can I still run Kafka?
A> Of course. Kafka is just a Java program. On any Linux VM you need Java 17 or newer and the Kafka download. If you have nothing at all, Google Colab gives you a free Linux machine in the browser.
K> And what do we build?
A> Two things companies really build: a <b>live order dashboard</b> for TiffinGo, and a <b>UPI fraud alert pipeline</b> where one service’s output topic is the next service’s input. Every command below was run, and the Colab notebook was executed end to end.
  </div>
</section>
'''

lv = '''
LEVELS> The projects at three levels
L1> Just run them
      <ul>
        <li>Open the Colab notebook, press <b>Run all</b>, and watch both projects print results.</li>
      </ul>
L2> Understand the moving parts
      <ul>
        <li>Project 1: one topic, one producer, one consumer group that keeps <b>state</b> (running totals) in memory.</li>
        <li>Project 2: <b>two topics</b> chained by a service that is both a consumer and a producer. The SMS notifier depends only on the <code>fraud-alerts</code> topic, not on the detector’s code.</li>
      </ul>
L3> What would change in production
      <ul>
        <li>In-memory state is lost on restart; Kafka Streams keeps state in fault-tolerant stores (Lesson 9.2).</li>
        <li>Detector writes and offset commits are separate; a crash can duplicate an alert. Transactions make read-process-write exactly-once (Lesson 3.5).</li>
        <li>Rules need tuning: in our run a genuine user with 5 small payments in a minute was also flagged.</li>
      </ul>
/LEVELS
'''
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>A real-time pipeline</h2>
''' + def_block(
    'A <b>real-time (streaming) pipeline</b> processes events continuously as they arrive rather than in periodic batches. In Kafka it is composed of <b>producers</b> that publish events to topics, <b>stream processors</b> (consumers that transform, aggregate or filter events and may publish results to further topics), and <b>sinks</b> that act on the results. Each stage is an independent consumer group, so stages scale, fail and evolve independently, and intermediate topics decouple them.',
    'Events flow through small programs connected by topics. Each program reads one topic, does one job and, if needed, writes to the next topic. You can add, restart or change one program without touching the others.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Stream processor', 'Consumer that computes results.'),
    ('Sink', 'Stage that acts on results.'),
    ('Stateful', 'Remembers past events (totals, windows).'),
    ('Sliding window', 'Last N seconds of events.'),
    ('Chained topics', 'Output of one stage feeds the next.'),
    ('Colab', 'Free Linux notebook in the browser.'),
    ('KRaft standalone', 'Single-node format option.'),
    ('JSON event', 'Value encoded as JSON text.'),
]) + '''

  <h3>Why, how, where</h3>
''' + WHW + '''

  <h3>Concept map: what depends on what</h3>
''' + MAP + '''

  <h3>The two projects</h3>
''' + p1_svg() + p2_svg() + lv + myths([
    ('You need Docker or a big server to learn Kafka.', 'Kafka runs on any machine with Java 17+; even free Colab works.', 'the notebook ran end to end; Kafka started in about 15 seconds.'),
    ('Kafka itself detects fraud or computes totals.', 'Kafka stores and moves events; your consumers (or Kafka Streams) compute.', 'p2_fraud_detector.py holds the rules.'),
    ('A pipeline means one big program.', 'Small services connected by topics, each in its own consumer group.', 'the notifier only reads fraud-alerts.')]) + '''
EXAM> “Design a real-time alert system with Kafka.” Producers publish raw events keyed by entity; a processor group consumes, applies rules (often with windowed state) and publishes alerts to a separate topic; notification services consume alerts. Discuss partitioning by key, lag monitoring, state recovery and duplicate handling (idempotence/transactions).
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>VM or Colab?</h2>
''' + table(['', 'Linux VM (Ubuntu)', 'Google Colab'], [
    ['Cost', 'free (own PC/VirtualBox) or cloud VM', 'free'],
    ['Setup time', '10 minutes', 'Run all, about 2 minutes'],
    ['Lasts', 'until you delete it', 'until the session ends (resets)'],
    ['Many terminals', 'yes (open several SSH windows)', 'one notebook; background via subprocess'],
    ['Best for', 'practising like production', 'quick learning, no install'],
], minw=560) + '''
WARN> In Jupyter and Colab, <code>!command &amp;</code> (a shell background job) is not reliable: our test raised “Background processes not supported”. The notebook therefore starts Kafka and the producer with Python’s <code>subprocess.Popen</code>. Also, Kafka 4.x needs <b>Java 17 or newer</b>; older Java fails at startup.
</section>
'''

steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Build both projects</h2>
  <p>All outputs are real. Steps 1–2 ran on Ubuntu 24.04 with OpenJDK 21 (the same commands work on any Ubuntu VM; on Colab use the notebook, which installs OpenJDK 17). Download: <a href="files/kafka_two_projects_colab.ipynb">Colab notebook</a> · <a href="files/kafka_projects.zip">all project files (.zip)</a>.</p>
''' + stepper([
    ('Step 1 · VM: install Java and Kafka',
     code('bash', 'terminal (VM)', 'sudo apt update && sudo apt install -y openjdk-21-jre-headless\njava -version\nwget https://downloads.apache.org/kafka/4.4.0/kafka_2.13-4.4.0.tgz\ntar -xzf kafka_2.13-4.4.0.tgz && cd kafka_2.13-4.4.0', sec(S, '$ java -version', '$ KAFKA_CLUSTER_ID')),
     'Any Java 17+ works. The download is about 130 MB. If a newer Kafka has been released, the 4.4.0 file moves to <code>archive.apache.org/dist/kafka/4.4.0/</code>.'),
    ('Step 2 · VM: format, start, create topics',
     code('bash', 'terminal (VM)', 'KAFKA_CLUSTER_ID="$(bin/kafka-storage.sh random-uuid)"\nbin/kafka-storage.sh format --standalone -t $KAFKA_CLUSTER_ID -c config/server.properties\nnohup bin/kafka-server-start.sh config/server.properties > kafka.log 2>&1 &\nbin/kafka-topics.sh --bootstrap-server localhost:9092 --create --topic orders --partitions 3\n# also: payments (3 partitions), fraud-alerts (1)\npip install confluent-kafka', sec(S, '$ KAFKA_CLUSTER_ID', drop=('Bootstrap metadata',))),
     '<code>format --standalone</code> prepares a single-node KRaft quorum. <code>nohup … &amp;</code> keeps Kafka running after you close the terminal. Three topics are ready.'),
    ('Step 3 · Colab: run the notebook',
     code('python', 'kafka_two_projects_colab.ipynb', '!apt-get -qq install -y openjdk-17-jre-headless\n!pip -q install confluent-kafka\n!wget -q https://downloads.apache.org/kafka/4.4.0/kafka_2.13-4.4.0.tgz && tar -xzf kafka_2.13-4.4.0.tgz\n%cd kafka_2.13-4.4.0\ncid = subprocess.check_output(["bin/kafka-storage.sh", "random-uuid"]).decode().split()[-1]\n!bin/kafka-storage.sh format --standalone -t {cid} -c config/server.properties\nkafka = subprocess.Popen(["bin/kafka-server-start.sh", "config/server.properties"],\n                         stdout=open("kafka.log", "w"), stderr=subprocess.STDOUT)', 'Kafka Server started\nCreated topic orders.\nCreated topic payments.\nCreated topic fraud-alerts.'),
     'Upload the notebook to colab.research.google.com (File → Upload notebook) and choose <b>Runtime → Run all</b>. We executed this notebook end to end with a Jupyter kernel; the output above is from that run.'),
    ('Step 4 · Project 1: the producer',
     code('python', 'p1_order_producer.py', src('p1_order_producer.py'), 'sent 50 orders'),
     'Each order is JSON with a key = city. <code>partitioner: murmur2_random</code> makes Python place keys exactly like Java clients (Lesson 1.4). <code>poll(0)</code> serves delivery callbacks; <code>flush()</code> waits until all are sent.'),
    ('Step 5 · Project 1: the live dashboard',
     code('python', 'p1_live_dashboard.py', src('p1_live_dashboard.py'), sec(P, '  ALERT big order o0002', '== project 1: lag check')),
     'Run the dashboard in one terminal and the producer in another (on Colab the producer runs in the background). Totals update every 10 orders, alerts appear instantly with their partition and offset. Mumbai and Bengaluru share partition 1; Pune and Delhi partition 0; partition 2 is empty.'),
    ('Step 6 · Project 1: check lag',
     code('bash', 'terminal', 'bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group live-dashboard', sec(P, '== project 1: lag check', '== project 2')),
     '18 + 32 = 50 orders read, lag 0: the dashboard is fully caught up.'),
    ('Step 7 · Project 2: payments and the fraud detector',
     code('python', 'p2_fraud_detector.py', src('p2_fraud_detector.py'), sec(P, '$ python p2_fraud_detector.py', '$ python p2_notifier.py')),
     'The detector keeps, per UPI id, the timestamps of the last 60 seconds (a <b>sliding window</b>) and checks two rules. Flagged payments are <b>produced</b> to <code>fraud-alerts</code>: this program is a consumer and a producer. user9’s burst and user3’s Rs 75,000 payment were caught; user1 was also flagged for 5 small payments in a minute, a false positive you would tune.'),
    ('Step 8 · Project 2: the notifier',
     code('python', 'p2_notifier.py', src('p2_notifier.py'), sec(P, '$ python p2_notifier.py', '== project 2: groups')),
     'A separate service in its own group reads only <code>fraud-alerts</code>. It never imports the detector. Tomorrow a “block card” service can subscribe to the same topic without any change here.'),
]) + '''
</section>
'''

see = [
    term([('Kafka Server started', G), ('Created topic orders.', W), ('Created topic payments.', W), ('Created topic fraud-alerts.', W)], size=7.2),
    term([('[ 10 orders] Bengaluru: 4 / Rs 1860  Mumbai: 6 / Rs 1830', W), ('ALERT big order o0029 Pune Rs 1500', Y), ('[ 50 orders] Bengaluru: 17 / Rs 7870 ...', G)], size=6.6),
    term([('FLAG t034 user9@upi Rs 4999: >4 in 60 s', RD), ('FLAG t045 user3@upi Rs 75000: > Rs 50,000', RD), ('checked 60 payments, raised 6 alerts', W)], size=6.8),
    term([('SMS to user9@upi: payment t034 held', G), ('SMS to user3@upi: payment t045 held', G)], size=7.0),
]
B1 = [
    t(180, 14, 'One KRaft node, three topics', 9, bold=True) + opbox(130, 40, 'Kafka 4.4', 'standalone', 'acc', 100, 34) + ''.join(opbox(20 + k * 112, 96, n, '', 'blue', 100, 24) for k, n in enumerate(['orders', 'payments', 'fraud-alerts'])) + cap('Ready in ~15 s.', '', 'green', y=144, h=30),
    t(180, 14, 'Project 1: stateful consumer', 9, bold=True) + opbox(10, 50, 'producer', 'key=city', 'acc', 90, 34) + arrow(100, 67, 130, 67, 'ink3', 1) + opbox(130, 50, 'orders', '3 partitions', 'blue', 90, 34) + arrow(220, 67, 250, 67, 'ink3', 1) + opbox(250, 50, 'dashboard', 'totals in memory', 'green', 100, 34) + cap('Totals update live.', '', 'green', y=144, h=30),
    t(180, 14, 'Project 2: consume → produce', 9, bold=True) + opbox(10, 50, 'payments', '', 'blue', 80, 30) + arrow(90, 65, 120, 65, 'ink3', 1) + opbox(120, 44, 'detector', '60 s window', 'card', 100, 40) + arrow(220, 65, 250, 65, 'red', 1) + opbox(250, 50, 'fraud-alerts', '6 alerts', 'red', 100, 30) + cap('A processor is both.', '', 'red', y=144, h=30),
    t(180, 14, 'Independent sink', 9, bold=True) + opbox(40, 50, 'fraud-alerts', '', 'red', 110, 30) + arrow(150, 65, 200, 65, 'ink3', 1) + opbox(200, 46, 'sms-notifier', 'own group', 'green', 120, 38) + cap('No code link to the detector.', '', 'blue', y=144, h=30),
]
two = anim_two('Two real-time projects', 'Run, stream, alert', 'Real outputs from the run', 'How the pipeline is wired', see, B1,
               ['Kafka up.', 'Dashboard.', 'Detector.', 'Notifier.'], ['Setup.', 'Stateful.', 'Chained.', 'Decoupled.'])
PEEL = peel('One UPI payment through the fraud pipeline', 'Payment t045 (Rs 75,000), stage by stage. (Our run.)',
    [('Producer', ''), ('payments topic', ''), ('Detector reads', ''), ('Rule fires', ''), ('fraud-alerts topic', ''), ('Notifier', '')],
    [['Producer', 'key user3@upi', 'value {txn t045,', 'amount 75000}'],
     ['payments topic', 'murmur2(key) → one', 'partition, next offset', 'stored for 7 days'],
     ['Detector reads', 'group fraud-detector', 'updates user3’s', '60 s window'],
     ['Rule fires', 'amount > 50,000', 'reason added', 'to the event'],
     ['fraud-alerts topic', 'detector PRODUCES', 'the alert, key user3', 'commits its offset'],
     ['Notifier', 'group sms-notifier', 'prints the SMS', 'lag back to 0']],
    ['Send.', 'Store.', 'Read.', 'Detect.', 'Publish.', 'Notify.'], 'scenario-peel')

def five(kind, title, sub, cons, lines, caps, hid):
    fr = [t(180, 22, a, 9.4, 'acc' if i == 4 else 'ink', bold=True) + t(180, 56, b, 8.4, 'ink2') + cap(c, '', tone, y=150, h=34) for i, (a, b, c, tone) in enumerate(lines)]
    return anim_one(kind, title, sub, cons[0], cons[1], fr, caps, hid=hid)
s1 = five('Real-time scenario 1', 'Dashboard restarts mid-sale', 'Stateful consumer recovery. (Typical.)',
          ('State recovery', 'Offsets survive a restart; in-memory totals do not'), [
    ('Dashboard pod restarts', 'during evening peak', 'Totals reset to 0!', 'red'),
    ('Offsets were committed', 'resumes after last read', 'Old orders skipped.', 'amber'),
    ('Option 1', 'new group, earliest: rebuild', 'Slow but simple.', 'green'),
    ('Option 2', 'Kafka Streams state store', 'Lesson 9.2.', 'green'),
    ('Lesson', 'state needs a plan', 'Not just offsets.', 'blue')],
    ['Restart.', 'Offsets.', 'Rebuild.', 'Streams.', 'Plan.'], 'scenario-state')
s2 = five('Real-time scenario 2', 'Too many false alerts', 'Tuning a rule without stopping the pipeline. (Typical.)',
          ('Replay to tune', 'Re-run a new rule version from history in a new group'), [
    ('Users complain', 'small payments held', 'Like user1 in our run.', 'red'),
    ('Write rule v2', '> 4 payments AND total > Rs 5,000', 'Stricter.', 'blue'),
    ('Run v2 as new group', 'fraud-detector-v2, earliest', 'Replays 7 days.', 'green'),
    ('Compare alert counts', 'v1 vs v2', 'Measured, not guessed.', 'green'),
    ('Switch notifier', 'to v2 alerts topic', 'Zero downtime.', 'blue')],
    ['Complaints.', 'Rule v2.', 'Replay.', 'Compare.', 'Switch.'], 'scenario-tune')
s3 = five('Real-time scenario 3 · advanced', 'Duplicate SMS after a crash', 'Read-process-write without transactions. (Typical.)',
          ('Exactly-once', 'Use Kafka transactions to commit the alert and the input offset together'), [
    ('Detector produces alert', 'then crashes', 'Before committing offset.', 'red'),
    ('Restart re-reads t045', 'produces alert again', 'Duplicate.', 'red'),
    ('Customer gets 2 SMS', 'confusing', 'At-least-once.', 'amber'),
    ('Transactions', 'alert + offset atomically', 'Lesson 3.5.', 'green'),
    ('Or idempotent notifier', 'skip seen txn ids', 'Practical fix.', 'blue')],
    ['Crash.', 'Re-read.', 'Duplicate.', 'Transactions.', 'Idempotent.'], 'scenario-eos')
animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Run, stream, alert</h2>
  <p>Left: real outputs from our run. Right: how the pipeline is wired.</p>
''' + two + '''
  <p>Now peel one payment through the whole pipeline.</p>
''' + PEEL + '''
  <p>Three live scenarios follow: a restart, rule tuning, and duplicates.</p>
''' + s1 + s2 + s3 + '''
</section>
'''

def uc_(word, sub, tone, title, desc, flow_):
    return usecase(f'<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-{tone}" style="stroke:var(--{tone if tone != "acc" else "track"})"/>' + t(60, 42, word, 11, tone, bold=True) + t(60, 58, sub, 7.4, 'ink2'), title, desc, flow_)
uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Projects like these at work</h2>
''' + '\n'.join([
    uc_('food', 'live ops', 'blue', '1. Live operations dashboard', 'Orders per city per minute on a big screen in the ops room.', ['Orders', '*consumer', 'Dashboard']),
    uc_('UPI', 'fraud', 'red', '2. Payment risk checks', 'Rules and models score payments in real time and hold risky ones.', ['Payments', '*detector', 'Hold + SMS']),
    uc_('IoT', 'cold chain', 'violet', '3. Cold-chain alerts', 'Fridge sensors stream temperatures; alerts fire above a threshold.', ['Sensors', '*rules', 'Alerts']),
    uc_('ride', 'ETA', 'green', '4. Delivery ETA updates', 'GPS events update ETAs and notify customers.', ['GPS', '*processor', 'App push']),
    uc_('shop', 'stock', 'acc', '5. Low-stock alerts', 'Sales events update stock; alerts trigger re-ordering.', ['Sales', '*state', 'Re-order']),
]) + '''
  <p class="muted">Examples are simplified descriptions of common patterns; our projects use generated data.</p>
</section>
'''
pre = '''<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> finish Lessons 1.1–1.5. You need either a Linux VM (Ubuntu 22.04/24.04, 2 GB RAM, Java 17+) or a Google account for Colab. Files: <a href="files/kafka_two_projects_colab.ipynb">Colab notebook</a> · <a href="files/kafka_projects.zip">project files</a>.</p></div>
'''
body = story.replace('  <div class="story">', pre + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + steps + animation + uc
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
