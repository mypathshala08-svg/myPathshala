import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from svgkit import scn
BODY = body(HERE)
META = dict(module='12-capstone', lesson='03-review-and-interview-preparation', n='12.3', module_label='Module 12 · Capstone',
    title='Capstone: review and interview preparation',
    desc='Capstone part 3: proving the pipeline under failure and preparing for interviews. A chaos test kills a broker during exactly-once processing and an independent audit finds all 6,000 orders exactly once; a review checklist covers data, durability, errors and operations; and an interview map links common Kafka questions to every lesson in the course.',
    og_desc='Kill a broker mid-processing, audit 6,000 orders: every one exactly once. Then the interview map.',
    minutes=24, level='Advanced',
    lead='Does the pipeline survive a broker dying mid-transaction? We <b>kill k3</b>, finish processing, and <b>audit every order</b>, then turn the course into an <b>interview plan</b>. <b>All outputs are real.</b>',
    chips=['k3 killed at t+2 s', '6,000 ids exactly once', 'Review checklist', 'Runs in your browser (Python)'])
MAIN = '''# Audit: every id exactly once across enriched + DLQ
enriched = list(range(1, 3729))                # pretend ids
dlq = list(range(3729, 6001))
expected = set(range(1, 6001))

all_ids = enriched + dlq
missing = expected - set(all_ids)
dupes = len(all_ids) - len(set(all_ids))
print("records", len(all_ids), "missing", len(missing), "duplicates", dupes)
print("exactly once:", not missing and dupes == 0)
'''
RUN = dict(heading='Run the code: the audit', intro='<p>The check behind “exactly once”. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('missing = expected - set(all_ids)', 'Completeness.'), ('dupes = len(all_ids) - len(set(all_ids))', 'Uniqueness.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>. Append a duplicate id.', code=None),
        dict(label='2 · Predict first: lab totals', hint='<b>Predict first:</b> 3,728 + 2,272.', code='print(3728 + 2272)\n'),
        dict(label='3 · Stop rule', hint='Stop on count, not on empty polls.', code='done, expected = 3000, 3000\nprint(done >= expected)\n'),
        dict(label='4 · Failures', hint='min ISR 2 with one broker dead.', code='print("writes continue:", 2 >= 2)\n'),
        dict(label='5 · Spot the error', hint='Coordinator moving.', expect='error', code='raise TimeoutError("COORDINATOR_NOT_AVAILABLE: retry after the group coordinator moves")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC: chaos + audit', intro='<p>After 12.2. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Run', cmd='python3 l123.py      # kills k3 after 2 s', file='terminal', output='  every id 1..6000 accounted exactly once: True', note='Then: docker start k3.'),
           dict(title='2 · Repeat', cmd='kill the processor instead (Ctrl-C mid-run), restart, audit again', file='terminal', output='', note='Your own drill.')])
TRACE = dict(heading='Audit step by step', intro='<p>Missing and duplicates.</p>',
    code='ids = [1, 2, 4]\nexpected = {1, 2, 3, 4}\nprint(expected - set(ids), len(ids) - len(set(ids)))\n', notes={3: 'Missing 3 :: Would fail.'})
WORKED_INTRO = 'Three review decisions.'
EXAMPLES = [
    dict(level='b', tag='Review · chaos', title='First drill', problem='<p>What to break first?</p>', inp='plan',
         approach=['Kill one broker mid-run.', 'Audit.', 'Then kill the processor.'], code='print(["broker", "processor", "network pause"])\n', notes={1: 'Order :: Simple first.'}, tryit='Types table.'),
    dict(level='i', tag='Review · loop', title='Stop condition', problem='<p>Job ended early during failover.</p>', inp='code',
         approach=['Stop on expected count or end offsets.', 'Generous deadline.', 'Log progress.'], code='print("while done < expected and time_left: …")\n', notes={1: 'Lesson :: Our first run.'}, tryit='Warning.'),
    dict(level='a', tag='Review · interview', title='Answer with evidence', problem='<p>“Is your pipeline exactly-once?”</p>', inp='answer',
         approach=['Explain the 3 parts.', 'Describe the chaos test.', 'Quote the audit.'], code='print("6,000 ids, each once, with a broker killed")\n', notes={1: 'Credible :: Numbers.'}, tryit='Interview 2.')]
QUIZ = mix([
    dict(q='Beginner: The audit checks…', options=['Speed', 'Every id present exactly once', 'Disk', 'ACLs'], answer=1, why='Completeness + uniqueness.'),
    dict(q='Beginner: Broker killed in the drill…', options=['k1', 'k3', 'none', 'all'], answer=1, why='t+2 s.'),
    dict(q='Beginner: Ids missing after the drill…', options=['195', '0', '3000', '12'], answer=1, why='Step 3.'),
    dict(q='Intermediate: Writes continued with one broker down because…', options=['acks=0', 'RF 3 with min ISR 2', 'Compaction', 'Luck'], answer=1, why='5.2.'),
    dict(q='Intermediate: Our first attempt processed nothing because…', options=['Data lost', 'Loop stopped on empty polls during failover', 'Wrong topic', 'ACLs'], answer=1, why='Level 3.'),
    dict(q='Intermediate: Aborted batch data is hidden by…', options=['read_uncommitted', 'read_committed', 'Compaction', 'Retention'], answer=1, why='3.5.'),
    dict(q='Advanced: A passing chaos test proves…', options=['Everything', 'Only the failures tried', 'Nothing', 'Performance'], answer=1, why='Keep testing.'),
    dict(q='Advanced: Best interview evidence…', options=['Buzzwords', 'Real numbers from tests', 'Slides', 'Certificates only'], answer=1, why='Credible.')])
REVISION = ['Chaos test + independent audit = proof.', 'Lab: k3 killed; 3,000 processed in 15 transactions; 6,000 ids exactly once.',
    'Lesson: stop loops on counts/deadlines, not empty polls.', 'Checklist: data, durability, errors, ops, security, DR.', 'Interview map: every module → typical questions.']
FAQ = [('How often should we run drills?', 'Before major releases and regularly (e.g. quarterly game days), plus automated tests in CI with a test cluster.'),
    ('Can I test without Docker?', 'Kafka Streams apps with TopologyTestDriver; client logic with mocks; but broker failures need a real cluster.'),
    ('What is the most common interview topic?', 'Delivery semantics (acks, idempotence, EOS), consumer groups and rebalances, and partitions/ordering.'),
    ('What next after this course?', 'Build your own pipeline, add Kafka Streams or Spark (Module 9), secure it (10.3) and add DR (10.4).')]
PRACTICE_INTRO = 'Review programs.'
PROBLEMS = [
    dict(level='easy', title='Missing', stmt='Find missing ids.', inp='sets', code='print({1, 2, 3, 4} - {1, 2, 4})\n', explain='{3}.'),
    dict(level='easy', title='Duplicates', stmt='Count duplicates.', inp='list', code='ids = [1, 1, 2]\nprint(len(ids) - len(set(ids)))\n', explain='1.'),
    dict(level='easy', title='Total', stmt='Enriched + DLQ.', inp='ints', code='print(3728 + 2272)\n', explain='6,000.'),
    dict(level='medium', title='Audit fn', stmt='Exactly once?', inp='list', code='def ok(ids, n): return sorted(ids) == list(range(1, n + 1))\nprint(ok([2, 1, 3], 3))\n', explain='True.'),
    dict(level='medium', title='Stop rule', stmt='Loop until count.', inp='ints', code='done = 0\nwhile done < 5: done += 2\nprint(done)\n', explain='6 ≥ 5.'),
    dict(level='medium', title='Checklist', stmt='Missing items.', inp='sets', code='need = {"DLQ", "EOS", "lag alert", "ACLs"}\nhave = {"DLQ", "EOS"}\nprint(need - have)\n', explain='Gaps.'),
    dict(level='business', title='Drill cost', stmt='1 hour × 4 drills/year.', inp='ints', code='print(4, "hours a year")\n', explain='Cheap insurance.'),
    dict(level='business', title='Risk', stmt='Orders/day × 0.1% dup at ₹200.', inp='ints', code='print(100000 * 0.001 * 200)\n', explain='₹20,000/day.')]
SCN_INTRO = 'Final interview questions.'
SCENARIOS = (scn('Any company · data', 'Fresher', '“How would you test a Kafka pipeline?”', 'Explain.', 'answer?', '<p>Unit-test logic, integration-test against a real cluster, then inject failures (kill a broker or the processor) and audit outputs with a read_committed reader: every record present exactly once.</p>', '“Run it once.”') +
    scn('Platform', 'Mid-level', 'Job ended early', 'During failover.', 'fix?', '<ul><li>Stop on counts/end offsets, not empty polls.</li></ul>', 'Shorter timeouts.') +
    scn('Fintech', 'Mid-level', 'Prove EOS', 'Auditor asks.', 'show?', '<ul><li>Chaos drill + audit results.</li><li>Configs: idempotence, transactions, read_committed.</li></ul>', 'Point at docs.') +
    scn('Architecture', 'Senior', 'Production readiness', 'Sign-off.', 'checklist?', '<ul><li>Data, durability, errors, ops, security, DR.</li><li>Evidence for each.</li></ul>', 'Gut feeling.'))
