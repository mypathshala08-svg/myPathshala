import os, sys, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
BODY = body(HERE)

META = dict(
    module='01-introduction', lesson='06-two-real-time-projects-vm-and-colab', n='1.6',
    module_label='Module 1 · Start here: why Kafka?',
    title='Two real-time projects: on a VM or in Colab',
    desc='Build two real-time Kafka projects step by step on a Linux VM or in free Google Colab: a TiffinGo live order dashboard (revenue per city and big-order alerts) and a UPI fraud alert pipeline (payments → fraud detector with a 60-second sliding window → fraud-alerts topic → SMS notifier). Kafka 4.4 KRaft from the binary, Python confluent-kafka, a downloadable Colab notebook, and real outputs.',
    og_desc='Kafka 4.4 on a VM or in Colab, plus two real-time projects with real outputs and a ready notebook.',
    minutes=40, level='Beginner',
    lead='Time to build. Run Kafka 4.4 on a <b>Linux VM</b> or in free <b>Google Colab</b>, then build a <b>live order dashboard</b> and a <b>UPI fraud alert pipeline</b>. Every command was run and the Colab notebook was executed end to end. <b>All outputs are real.</b>',
    chips=['VM or Colab', '2 projects', 'Downloadable notebook', 'Runs in your browser (Python)'],
)

MAIN = '''# The fraud detector's sliding-window rule, without Kafka
from collections import defaultdict, deque
payments = [("user9", 4999, 150), ("user9", 4999, 153), ("user9", 4999, 156),
            ("user9", 4999, 159), ("user9", 4999, 162), ("user3", 75000, 225),
            ("user2", 50, 230)]                     # (upi id, amount, seconds)
recent = defaultdict(deque)
for vpa, amount, ts in payments:
    q = recent[vpa]
    q.append(ts)
    while q and ts - q[0] > 60:                 # keep only the last 60 s
        q.popleft()
    if amount > 50000:
        print("FLAG", vpa, amount, "amount over Rs 50,000")
    elif len(q) > 4:
        print("FLAG", vpa, amount, "more than 4 payments in 60 s")
    else:
        print("ok  ", vpa, amount)
'''
RUN = dict(
    heading='Run the code: the fraud rule',
    intro='<p>The detector’s logic on 7 payments. Press <b>Run</b>, then try the challenges.</p>',
    code=MAIN,
    anno=[
        ('    while q and ts - q[0] > 60:                 # keep only the last 60 s', 'A sliding window: drop timestamps older than 60 seconds.'),
        ('    elif len(q) > 4:', 'The velocity rule: more than 4 payments in the window.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then change the window to 5 seconds.', code=None),
        dict(label='2 · Predict first: totals', hint='<b>Predict first:</b> Mumbai revenue for orders 250 + 480 + 120?',
             code='''print(250 + 480 + 120)
'''),
        dict(label='3 · Dashboard', hint='Revenue per city from a list.',
             code='''from collections import defaultdict
rev = defaultdict(int)
for city, amt in [("Mumbai", 250), ("Pune", 480), ("Mumbai", 1500)]:
    rev[city] += amt
print(dict(rev))
'''),
        dict(label='4 · Tune', hint='Flag only if count > 4 AND total > 5000.',
             code='''window = [50, 50, 120, 50, 50]
print(len(window) > 4 and sum(window) > 5000)
'''),
        dict(label='5 · Spot the error', hint='Java version check.', expect='error',
             code='''java = 11
assert java >= 17, "Kafka 4.x requires Java 17 or newer (found 11)"
'''),
    ],
)
RUN['tasks'][0]['code'] = RUN['code']

PCRUN = dict(
    heading='Run on your PC: both projects',
    intro='<p>On a VM with Kafka started (Steps 1–2). Use two terminals for Project 1. <b>Outputs are real.</b></p>',
    items=[
        dict(title='1 · Dashboard', cmd='python p1_live_dashboard.py', file='terminal 1',
             output='[ 50 orders] Bengaluru: 17 / Rs 7870  Delhi: 9 / Rs 3850  Mumbai: 15 / Rs 6220  Pune: 9 / Rs 2920', note='Start it first.'),
        dict(title='2 · Orders', cmd='python p1_order_producer.py 50', file='terminal 2',
             output='sent 50 orders', note='10 seconds of orders.'),
        dict(title='3 · Fraud pipeline', cmd='python p2_payment_producer.py && python p2_fraud_detector.py && python p2_notifier.py', file='terminal',
             output='checked 60 payments, raised 6 alerts\nSMS to user3@upi: payment t045 of Rs 75000 held for review (amount over Rs 50,000)', note='Three stages.'),
    ],
)

TRACE = dict(
    heading='The sliding window',
    intro='<p>Watch old timestamps fall out.</p>',
    code='''q = [100, 130, 150]
now = 175
while q and now - q[0] > 60:
    q.pop(0)
q.append(now)
print(q, len(q))
''',
    notes={3: 'Expire :: 175 − 100 > 60, drop 100.', 6: 'Count :: 3 payments in the last 60 s.'},
)

WORKED_INTRO = 'Three extensions to try after the projects.'
EXAMPLES = [
    dict(level='b', tag='Project 1', title='Add a per-city order count alert',
         problem='<p>Alert when a city exceeds 15 orders.</p>',
         inp='count per city',
         approach=['Keep counts (already there).', 'Check after each order.', 'Alert once per city.'],
         code='''count, alerted = {"Mumbai": 16}, set()
for c, n in count.items():
    if n > 15 and c not in alerted:
        alerted.add(c); print("ALERT", c, n)
''', notes={1: 'State :: Remember who was alerted.'},
         tryit='Step 5.'),
    dict(level='i', tag='Project 2', title='Add a “block card” service',
         problem='<p>Block UPI ids with 2 alerts in a day.</p>',
         inp='fraud-alerts topic',
         approach=['New consumer group block-service.', 'Count alerts per id.', 'No change to detector or notifier.'],
         code='''alerts = ["user9", "user9", "user3"]
from collections import Counter
print([u for u, n in Counter(alerts).items() if n >= 2])
''', notes={1: 'Decoupled :: Just another subscriber.'},
         tryit='Step 8.'),
    dict(level='a', tag='Project 2', title='Scale the detector',
         problem='<p>10× payments; one detector lags.</p>',
         inp='3 partitions',
         approach=['Run up to 3 detectors in one group.', 'Key = UPI id keeps each user’s window on one detector.', 'More partitions for more detectors.'],
         code='''partitions, detectors = 3, 3
print("each detector owns", partitions // detectors, "partition; windows stay correct (key = UPI id)")
''', notes={1: 'Keys :: Per-user state needs per-user partitioning.'},
         tryit='Lesson 1.2.'),
]

QUIZ = mix([
    dict(q='Beginner: Kafka 4.x needs which Java version?', options=['8', '11', '17 or newer', 'None'], answer=2,
         why='We used 21 on the VM, 17 on Colab.'),
    dict(q='Beginner: format --standalone prepares…', options=['A ZooKeeper', 'A single-node KRaft quorum', 'A topic', 'A consumer'], answer=1,
         why='Before first start.'),
    dict(q='Beginner: In Project 1 the dashboard is a…', options=['Producer', 'Consumer group live-dashboard', 'Broker', 'Topic'], answer=1,
         why='It reads orders.'),
    dict(q='Intermediate: The fraud detector is…', options=['Only a consumer', 'Both a consumer and a producer', 'A broker', 'A topic'], answer=1,
         why='Reads payments, writes alerts.'),
    dict(q='Intermediate: Why did partition 2 of orders stay empty?', options=['Broker down', 'Only 4 city keys', 'Retention', 'Colab limit'], answer=1,
         why='Lesson 1.4.'),
    dict(q='Intermediate: In Colab, Kafka is started with subprocess.Popen because…', options=['It is faster', '! background jobs are not supported', 'Java needs it', 'No reason'], answer=1,
         why='Our test raised the error.'),
    dict(q='Advanced: A detector crash after producing but before committing can cause…', options=['Lost payments', 'Duplicate alerts', 'Deleted topics', 'Nothing'], answer=1,
         why='Use transactions or idempotent sinks.'),
    dict(q='Advanced: To scale the detector and keep per-user windows correct, key payments by…', options=['Amount', 'UPI id', 'Random', 'Time'], answer=1,
         why='Same user → same partition → same detector.'),
])

REVISION = [
    'VM: Java 17+, download Kafka 4.4, format --standalone, start, create topics.',
    'Colab: notebook installs Java 17 + Kafka; start with subprocess.Popen.',
    'Project 1: orders → live-dashboard (revenue per city, alert ≥ Rs 1,000); lag 0.',
    'Project 2: payments → fraud-detector (60 s window, > Rs 50,000) → fraud-alerts → sms-notifier.',
    'Real run: 60 payments, 6 alerts (incl. a false positive).',
    'Production: state stores, transactions, monitoring.',
]
FAQ = [
    ('Will Kafka keep running if I close Colab?', 'No. The Colab machine is recycled; run the notebook again next time.'),
    ('Can I use VirtualBox on Windows as the VM?', 'Yes: install Ubuntu in VirtualBox (2 GB RAM is enough for these projects), then follow Steps 1–2.'),
    ('Why confluent-kafka and not kafka-python?', 'confluent-kafka wraps librdkafka, is actively maintained and fast. Remember to set partitioner=murmur2_random to match Java clients.'),
    ('How do I stop Kafka?', 'bin/kafka-server-stop.sh on the VM; in Colab, kafka.terminate() or restart the runtime.'),
]

PRACTICE_INTRO = 'Programs that extend the projects.'
PROBLEMS = [
    dict(level='easy', title='Average order', stmt='Average order value per city.', inp='revenue, count',
         code='''rev, cnt = {"Mumbai": 6220}, {"Mumbai": 15}
print({c: round(rev[c] / cnt[c], 1) for c in rev})
''', explain='Add to the dashboard.'),
    dict(level='easy', title='Big orders', stmt='Count orders ≥ 1000.', inp='amounts',
         code='''print(sum(a >= 1000 for a in [120, 1500, 250, 1500]))
''', explain='2 alerts.'),
    dict(level='easy', title='JSON event', stmt='Build an order event.', inp='fields',
         code='''import json
print(json.dumps({"order_id": "o0001", "city": "Pune", "amount": 250}))
''', explain='Value bytes.'),
    dict(level='medium', title='Top city', stmt='City with highest revenue.', inp='dict',
         code='''rev = {"Bengaluru": 7870, "Delhi": 3850, "Mumbai": 6220, "Pune": 2920}
print(max(rev, key=rev.get))
''', explain='Bengaluru in our run.'),
    dict(level='medium', title='Window count', stmt='Payments in last 60 s at t=200.', inp='times',
         code='''ts = [100, 150, 170, 190, 199]
print(sum(200 - t <= 60 for t in ts))
''', explain='4.'),
    dict(level='medium', title='Alert reasons', stmt='Count alerts per reason.', inp='list',
         code='''from collections import Counter
print(Counter(["velocity"] * 5 + ["amount"]))
''', explain='5 velocity, 1 amount.'),
    dict(level='business', title='Fraud saved', stmt='Held Rs 75,000 + 2 × Rs 4,999.', inp='amounts',
         code='''print(75000 + 2 * 4999)
''', explain='Value of the alerts.'),
    dict(level='business', title='False positive rate', stmt='2 of 6 alerts were genuine users.', inp='2, 6',
         code='''print(round(100 * 2 / 6), "%")
''', explain='Tune rules (Scenario 2).'),
]

SCN_INTRO = 'Project questions interviewers love.'
SCENARIOS = (
    scn('Any company · data', 'Fresher', '“Tell me about a Kafka project.”',
        'Describe Project 2.',
        'answer?',
        '<p>I built a UPI fraud alert pipeline: a producer streams payments keyed by UPI id; a fraud-detector consumer keeps a 60-second window per user and flags velocity and high-amount payments, publishing alerts to a fraud-alerts topic; an SMS notifier in its own group consumes alerts. On 60 test payments it raised 6 alerts, which taught me rule tuning.</p>', 'Only naming tools.') +
    scn('Data engineering', 'Mid-level', 'Restart',
        'Your dashboard lost totals after a restart.',
        'fix?',
        '''<ul>
          <li>State was in memory; offsets were committed.</li>
          <li>Rebuild from earliest in a new group, or use Kafka Streams state stores.</li>
        </ul>''', '“Kafka lost the data.”') +
    scn('Fintech', 'Mid-level', 'Scaling',
        'Payments grow 10×.',
        'plan?',
        '''<ul>
          <li>More partitions, more detectors in one group.</li>
          <li>Key by UPI id so windows stay correct.</li>
          <li>Monitor lag.</li>
        </ul>''', 'One bigger detector machine only.') +
    scn('Platform', 'Senior', 'Duplicates',
        'Customers sometimes get two fraud SMS.',
        'design?',
        '''<ul>
          <li>Transactions for read-process-write.</li>
          <li>Idempotent notifier keyed by txn id.</li>
          <li>Measure duplicates.</li>
        </ul>''', 'Ignoring it.')
)
