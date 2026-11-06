import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from svgkit import scn
BODY = body(HERE)
META = dict(module='02-producers', lesson='04-acks-and-durability', n='2.4', module_label='Module 2 · Producers',
    title='acks and durability',
    desc='Kafka producer acks=0, 1 and all, the ISR, min.insync.replicas, NOT_ENOUGH_REPLICAS, high watermark, unclean leader election and eligible leader replicas. Real Kafka 4.4 lab: 58k vs 49k vs 37k records/s for acks 0/1/all, then a stopped broker makes acks=all refuse writes while acks=1 accepts and acks=0 returns no offset.',
    og_desc='acks=0, 1, all measured, then a broker stopped: Kafka refuses unsafe writes. The durability recipe explained.',
    minutes=26, level='Intermediate',
    lead='How safe is “sent”? We measure the <b>speed of acks=0, 1 and all</b>, then stop a broker and watch Kafka <b>refuse</b> acks=all writes while acks=1 and acks=0 carry on. You will leave with the durability recipe most companies use. <b>All outputs are real.</b>',
    chips=['acks 0 / 1 / all measured', 'NOT_ENOUGH_REPLICAS live', 'RF 3 + min ISR 2', 'Runs in your browser (Python)'])
MAIN = '''# What each acks level waits for, and when it refuses
def write(acks, isr, min_isr):
    if acks == "all" and len(isr) < min_isr:
        return "NOT_ENOUGH_REPLICAS (refused)"
    if acks == "0":
        return "sent, no answer (offset unknown)"
    if acks == "1":
        return f"OK after leader {isr[0]}"
    return f"OK after all ISR {isr}"

for isr in ([1, 2, 3], [1, 2], [1]):
    print("ISR", isr)
    for acks in ("0", "1", "all"):
        print(f"   acks={acks:3} ->", write(acks, isr, min_isr=2))
'''
RUN = dict(heading='Run the code: acks rules', intro='<p>The leader’s decision in a few lines. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('    if acks == "all" and len(isr) < min_isr:', 'The safety floor: refuse instead of risking data.'), ('    return f"OK after all ISR {isr}"', 'acks=all waits for every in-sync replica.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>. Then set min_isr=3.', code=None),
        dict(label='2 · Predict first: tolerance', hint='<b>Predict first:</b> RF 3, min ISR 2: how many brokers can fail with writes continuing?', code='rf, min_isr = 3, 2\nprint(rf - min_isr)\n'),
        dict(label='3 · Throughput cost', hint='37,133 vs 58,005.', code='print(round(100 * (1 - 37133 / 58005)), "% slower")\n'),
        dict(label='4 · Copies', hint='Copies guaranteed for an acked record.', code='for min_isr in (1, 2, 3):\n    print(min_isr, "->", min_isr, "copies at least")\n'),
        dict(label='5 · Spot the error', hint='Refused write.', expect='error', code='isr, min_isr = [1, 2], 3\nif len(isr) < min_isr:\n    raise RuntimeError("Broker: Not enough in-sync replicas")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC: measure acks', intro='<p>Needs a 3-broker cluster (Lesson 1.3 lab). <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Perf test', cmd='kafka-producer-perf-test.sh --topic pay-24 --num-records 200000 --record-size 200 --throughput -1 --producer-props bootstrap.servers=k1:9092 acks=all', file='terminal', output='200000 records sent, 37133.308578 records/sec (7.08 MB/sec) …', note='Repeat with acks=0 and 1.'),
           dict(title='2 · Safety floor', cmd='kafka-configs.sh --bootstrap-server k1:9092 --entity-type topics --entity-name pay-24 --alter --add-config min.insync.replicas=2', file='terminal', output='Completed updating config for topic pay-24.', note='Topic level.'),
           dict(title='3 · Producer', cmd='Producer({"bootstrap.servers": "k1:9092", "acks": "all", "enable.idempotence": True})', file='python', output='offset 4, 5', note='Defaults already.')])
TRACE = dict(heading='Will this write succeed?', intro='<p>Check ISR against the floor.</p>',
    code='isr = [1, 2, 3]\nmin_isr = 2\nisr.remove(3)\nok = len(isr) >= min_isr\nisr.remove(2)\nok2 = len(isr) >= min_isr\nprint(ok, ok2)\n',
    notes={3: 'One down :: ISR 2, still OK.', 6: 'Two down :: ISR 1, refused.'})
WORKED_INTRO = 'Three durability decisions.'
EXAMPLES = [
    dict(level='b', tag='Durability · recipe', title='Configure a payments topic', problem='<p>No acknowledged payment may be lost.</p>', inp='topic + producer',
         approach=['RF 3, min ISR 2.', 'acks=all, idempotence on.', 'Unclean election off.'], code='topic = {"replication.factor": 3, "min.insync.replicas": 2, "unclean.leader.election.enable": False}\nproducer = {"acks": "all", "enable.idempotence": True}\nprint(topic, producer)\n', notes={1: 'Recipe :: Survives one broker loss.'}, tryit='Dissection.'),
    dict(level='i', tag='Durability · trade-off', title='Pick acks per topic', problem='<p>Orders, logs and GPS share a cluster.</p>', inp='topics',
         approach=['Orders: all.', 'Logs: 1.', 'GPS: 0.'], code='print({"orders": "all", "logs": "1", "gps": "0"})\n', notes={1: 'Per use :: Not one size for all.'}, tryit='Types table.'),
    dict(level='a', tag='Durability · ops', title='Plan maintenance safely', problem='<p>Can we restart a broker during the day?</p>', inp='RF, min ISR',
         approach=['Check RF − min ISR ≥ 1.', 'Check no under-replicated partitions first.', 'Restart one at a time.'], code='rf, min_isr = 3, 2\nprint("safe to restart one broker:", rf - min_isr >= 1)\n', notes={1: 'Ops :: Configuration decides downtime.'}, tryit='Scenario 2.')]
QUIZ = mix([
    dict(q='Beginner: acks=all waits for…', options=['Nothing', 'The leader', 'All in-sync replicas', 'Consumers'], answer=2, why='ISR.'),
    dict(q='Beginner: The default acks in Kafka 3.0+ is…', options=['0', '1', 'all', 'none'], answer=2, why='With idempotence.'),
    dict(q='Beginner: Fastest but riskiest is…', options=['acks=0', 'acks=1', 'acks=all', 'acks=2'], answer=0, why='No answer at all.'),
    dict(q='Intermediate: ISR 2, min.insync.replicas 3, acks=all →', options=['Success', 'NOT_ENOUGH_REPLICAS', 'Timeout only', 'Data loss'], answer=1, why='Step 3.'),
    dict(q='Intermediate: Recommended for important topics:', options=['RF 1', 'RF 3, min ISR 2', 'RF 3, min ISR 3', 'RF 2, min ISR 2'], answer=1, why='Survives one failure.'),
    dict(q='Intermediate: acks=0 delivery reports show offset…', options=['0', 'None / -1', 'The real offset', 'An error'], answer=1, why='No response.'),
    dict(q='Advanced: Consumers can read records only below…', options=['Log start', 'High watermark', 'Committed offset', 'Partition count'], answer=1, why='Replicated to ISR.'),
    dict(q='Advanced: Unclean leader election risks…', options=['Faster reads', 'Losing acknowledged data', 'Duplicates', 'Nothing'], answer=1, why='Out-of-sync leader.')])
REVISION = ['acks 0 / 1 / all = none / leader / all ISR.', 'Lab: 58,005 / 48,900 / 37,133 records/s.', 'min.insync.replicas: below it acks=all → NOT_ENOUGH_REPLICAS (writes stop, reads go on).',
    'Lab: ISR 2 < 3 → refused; acks=1 offsets 0,1; acks=0 offset None.', 'Recipe: RF 3, min ISR 2, acks=all, idempotence, unclean election off.', 'High watermark; ELR (KIP-966) in Kafka 4.x.']
FAQ = [('Is acks=all slow?', 'It adds the time for followers to fetch, usually a few milliseconds on a good network. Batching and compression recover most throughput.'),
    ('Does acks=all flush to disk?', 'No. Kafka relies on replication (copies in the page cache of several brokers) rather than fsync per write; flush settings exist but are rarely needed.'),
    ('Where is min.insync.replicas set?', 'As a broker default or per topic (kafka-configs.sh). It has no effect on acks=0 or 1.'),
    ('What does Elr mean in --describe?', 'Eligible Leader Replicas (KIP-966): replicas known to have all committed data that may safely become leader even if not in the current ISR.')]
PRACTICE_INTRO = 'acks and replication programs.'
PROBLEMS = [
    dict(level='easy', title='Failures tolerated', stmt='RF − min ISR.', inp='3, 2', code='print(3 - 2)\n', explain='1 broker.'),
    dict(level='easy', title='Slowdown', stmt='acks=all vs acks=1.', inp='37133, 48900', code='print(round(100 * (1 - 37133 / 48900)), "%")\n', explain='About 24%.'),
    dict(level='easy', title='Write allowed?', stmt='ISR 1, min 2.', inp='1, 2', code='print(1 >= 2)\n', explain='Refused.'),
    dict(level='medium', title='Pick acks', stmt='Map topics to acks.', inp='types', code='for t in ["payments", "logs", "gps"]:\n    print(t, {"payments": "all", "logs": "1", "gps": "0"}[t])\n', explain='By risk.'),
    dict(level='medium', title='ISR after failures', stmt='Remove failed brokers.', inp='[1,2,3], {3}', code='print([b for b in [1, 2, 3] if b not in {3}])\n', explain='[1, 2].'),
    dict(level='medium', title='Disk cost of RF', stmt='1 TB data at RF 3.', inp='1 TB', code='print(1 * 3, "TB")\n', explain='Durability costs disk.'),
    dict(level='business', title='Loss estimate', stmt='acks=1, 200 unreplicated payments × Rs 500 lost on crash.', inp='numbers', code='print("Rs", 200 * 500)\n', explain='Why payments use all.'),
    dict(level='business', title='Throughput needed', stmt='Peak 20k payments/s vs 37k/s capacity.', inp='numbers', code='print("headroom:", round(37133 / 20000, 1), "x")\n', explain='acks=all fits.')]
SCN_INTRO = 'Durability interview questions.'
SCENARIOS = (scn('Any company · data', 'Fresher', '“Explain acks.”', 'Compare 0, 1, all.', 'answer?', '<p>acks=0: no acknowledgement, may lose silently. acks=1: leader wrote it; lost if the leader dies before replication. acks=all: all in-sync replicas have it; with RF 3 and min.insync.replicas 2 it survives a broker loss.</p>', '“acks=all writes to all brokers in the cluster.”') +
    scn('Fintech', 'Mid-level', 'NOT_ENOUGH_REPLICAS', 'Producers get NOT_ENOUGH_REPLICAS.', 'diagnose?', '<ul><li>ISR below min.insync.replicas.</li><li>Check down/slow brokers, under-replicated partitions.</li><li>Do not lower the floor for payments.</li></ul>', 'Switching to acks=1.') +
    scn('Platform', 'Mid-level', 'Config review', 'Topic RF 3 with min ISR 3.', 'risk?', '<ul><li>Any restart blocks writes.</li><li>Use min ISR 2.</li></ul>', '“Maximum safety is always best.”') +
    scn('Platform', 'Senior', 'Total outage', 'All ISR replicas of a partition are lost.', 'options?', '<ul><li>Wait for an ISR replica (no loss, downtime).</li><li>Unclean election (availability, loss).</li><li>Decide per topic; ELR helps in 4.x.</li></ul>', 'Always enabling unclean election.'))
