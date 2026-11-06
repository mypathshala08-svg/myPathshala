import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from svgkit import scn
BODY = body(HERE)
META = dict(module='08-schemas', lesson='02-schema-evolution-and-compatibility', n='8.2', module_label='Module 8 · Schemas',
    title='Schema evolution and compatibility',
    desc='How to change Kafka message schemas safely: writer and reader schemas, defaults, Avro schema resolution, BACKWARD, FORWARD, FULL, NONE and transitive compatibility modes, type promotion, renames with aliases, deploy order, and Protobuf/JSON Schema notes. Real lab: a 409 for a field without a default, and a 6-change × 4-mode compatibility matrix from Schema Registry 8.1.',
    og_desc='Why one missing default causes HTTP 409: a real 6 × 4 schema compatibility matrix.',
    minutes=22, level='Advanced',
    lead='Which schema changes are safe, and for whom? We get a <b>409</b>, fix it with a <b>default</b>, and test <b>6 changes in 4 modes</b>, then prove the answers on real Avro bytes. <b>All outputs are real.</b>',
    chips=['HTTP 409 → 200', '6 × 4 matrix', 'Reader vs writer', 'Runs in your browser (Python)'])
MAIN = '''# Avro-style resolution: match fields by name, use reader defaults
def resolve(data, writer_fields, reader):
    out = {}
    for name, default in reader.items():
        if name in writer_fields:
            out[name] = data[name]
        elif default is not None:
            out[name] = default
        else:
            raise ValueError(f"No default value for field {name}")
    return out                     # extra writer fields are skipped

v1_data = {"id": 1, "item": "idli", "qty": 2}
v2_reader = {"id": None, "item": None, "qty": None, "spicy": False}
print(resolve(v1_data, v1_data.keys(), v2_reader))
'''
RUN = dict(heading='Run the code: schema resolution', intro='<p>How a reader handles missing fields. Press <b>Run</b>, then try the challenges.</p>', code=MAIN,
    anno=[('        elif default is not None:', 'Missing in data: use the reader default.'), ('    return out                     # extra writer fields are skipped', 'Old readers ignore new fields.')],
    tasks=[dict(label='1 · Run it', hint='Press <b>Run</b>. Set spicy default to None.', code=None),
        dict(label='2 · Predict first: safe everywhere', hint='<b>Predict first:</b> which change passed all 4 modes?', code='print("add field WITH default")\n'),
        dict(label='3 · Deploy order', hint='Mode → who upgrades first.', code='print({"BACKWARD": "consumers", "FORWARD": "producers", "FULL": "any"})\n'),
        dict(label='4 · Promotion', hint='Can a long reader read int data?', code='promo = {"int": ["long", "float", "double"]}\nprint("long" in promo["int"])\n'),
        dict(label='5 · Spot the error', hint='Reader field without default.', expect='error', code='raise ValueError("No default value for field city in in.tiffingo.Order")\n')])
RUN['tasks'][0]['code'] = RUN['code']
PCRUN = dict(heading='Run on your PC: test compatibility', intro='<p>Needs the registry from 8.1. <b>Outputs are real.</b></p>',
    items=[dict(title='1 · Set mode', cmd='curl -X PUT -H "Content-Type: application/vnd.schemaregistry.v1+json" localhost:8081/config/menu-82-value -d \'{"compatibility": "FULL"}\'', file='terminal', output='{"compatibility":"FULL"}', note='Per subject.'),
           dict(title='2 · Check', cmd='curl -X POST -H "Content-Type: application/vnd.schemaregistry.v1+json" "localhost:8081/compatibility/subjects/menu-82-value/versions/latest?verbose=true" -d @v2.json', file='terminal', output='{"is_compatible":true,"messages":[]}', note='Dry run.'),
           dict(title='3 · Versions', cmd='curl -s localhost:8081/subjects/menu-82-value/versions', file='terminal', output='[1,2]', note='History.')])
TRACE = dict(heading='Reading old data with v2', intro='<p>Match, default, skip.</p>',
    code='data = {"id": 1, "qty": 2}\nreader = {"id": None, "qty": None, "spicy": False}\nout = {k: data.get(k, d) for k, d in reader.items()}\nprint(out)\n',
    notes={3: 'Resolve :: spicy filled from default.'})
WORKED_INTRO = 'Three evolution decisions.'
EXAMPLES = [
    dict(level='b', tag='Evolution · add', title='Add an optional field', problem='<p>Add a coupon code.</p>', inp='field',
         approach=['Union with null.', 'Default null.', 'Compatible in all modes.'], code='print({"name": "coupon", "type": ["null", "string"], "default": None})\n', notes={1: 'Pattern :: Optional field.'}, tryit='Matrix row 1.'),
    dict(level='i', tag='Evolution · mode', title='Pick a mode', problem='<p>Shared topic, unknown upgrade order.</p>', inp='need',
         approach=['FULL_TRANSITIVE.', 'Only defaulted adds/deletes.', 'Any deploy order.'], code='print("FULL_TRANSITIVE")\n', notes={1: 'Safe :: Strictest.'}, tryit='Types table.'),
    dict(level='a', tag='Evolution · rename', title='Rename with aliases', problem='<p>qty → quantity.</p>', inp='schema',
         approach=['Reader field quantity with aliases ["qty"].', 'Or add-new/migrate/remove.', 'Registry may still refuse; test it.'], code='print({"name": "quantity", "type": "int", "aliases": ["qty"]})\n', notes={1: 'Alias :: Reader-side mapping.'}, tryit='Scenario 2.')]
QUIZ = mix([
    dict(q='Beginner: BACKWARD means…', options=['Old reads new', 'New reads old', 'No checks', 'Both'], answer=1, why='Default mode.'),
    dict(q='Beginner: The safest change is…', options=['Rename', 'Add field with default', 'Change type', 'Remove key'], answer=1, why='Y in all modes.'),
    dict(q='Beginner: Adding a field without default under BACKWARD gives…', options=['200', '409', '500', 'Nothing'], answer=1, why='Lab step 1.'),
    dict(q='Intermediate: Under BACKWARD, upgrade first…', options=['Producers', 'Consumers', 'Brokers', 'Registry'], answer=1, why='New readers first.'),
    dict(q='Intermediate: Widening int → long was allowed in…', options=['All modes', 'BACKWARD (and NONE)', 'FORWARD only', 'None'], answer=1, why='Old int reader fails.'),
    dict(q='Intermediate: An old reader on new data with an extra field…', options=['Fails', 'Skips the field', 'Crashes broker', 'Needs alias'], answer=1, why='By name.'),
    dict(q='Advanced: TRANSITIVE checks against…', options=['Latest only', 'All earlier versions', 'Next version', 'Nothing'], answer=1, why='Long history.'),
    dict(q='Advanced: Protobuf fields are matched by…', options=['Name', 'Number', 'Order in file', 'Type'], answer=1, why='Never reuse numbers.')])
REVISION = ['Writer vs reader schema; match by name; defaults fill missing; extras skipped.', 'BACKWARD new reads old (consumers first); FORWARD old reads new (producers first); FULL both.',
    'Lab: 409 without default, 200 with default (v2).', 'Matrix: add+default all; add no default FORWARD; delete BACKWARD; widen BACKWARD; rename/type change none.', 'TRANSITIVE for long-lived topics; breaking change → new topic.']
FAQ = [('Can I change the mode later?', 'Yes, per subject or globally via /config; it applies to future registrations.'),
    ('Does compatibility check meaning?', 'No, only structure. Unit changes need new fields or topics.'),
    ('Can I delete a version?', 'Soft and hard delete exist, but data written with it still needs it; avoid in production.'),
    ('What does Debezium do on ALTER TABLE?', 'Emits events with a new schema; with AvroConverter a new version is registered and must pass compatibility.')]
PRACTICE_INTRO = 'Evolution programs.'
PROBLEMS = [
    dict(level='easy', title='Mode', stmt='New reads old.', inp='str', code='print("BACKWARD")\n', explain='Default.'),
    dict(level='easy', title='Order', stmt='FORWARD deploy order.', inp='str', code='print("producers first")\n', explain='Old readers ok.'),
    dict(level='easy', title='Optional', stmt='Optional field type.', inp='list', code='print(["null", "string"])\n', explain='Default null.'),
    dict(level='medium', title='Resolve', stmt='Fill defaults.', inp='dicts', code='d = {"id": 1}\nr = {"id": None, "spicy": False}\nprint({k: d.get(k, v) for k, v in r.items()})\n', explain='spicy False.'),
    dict(level='medium', title='Check', stmt='Missing defaults in new fields.', inp='list', code='new = [{"name": "city"}, {"name": "spicy", "default": False}]\nprint([f["name"] for f in new if "default" not in f])\n', explain="['city']."),
    dict(level='medium', title='Promote', stmt='Is int → string a promotion?', inp='dict', code='promo = {"int": ["long", "float", "double"]}\nprint("string" in promo["int"])\n', explain='No.'),
    dict(level='business', title='Consumers', stmt='10 consumers, BACKWARD change.', inp='int', code='print("upgrade all 10 before producers")\n', explain='Plan.'),
    dict(level='business', title='Old data', stmt='Compacted topic, versions 1–5.', inp='str', code='print("BACKWARD_TRANSITIVE")\n', explain='All history.')]
SCN_INTRO = 'Evolution interview questions.'
SCENARIOS = (scn('Any company · data', 'Fresher', '“How do you add a field safely?”', 'Explain.', 'answer?', '<p>Give it a default (often a null union). Then new readers can read old data and old readers ignore the new field, so it passes BACKWARD, FORWARD and FULL.</p>', '“Just add it.”') +
    scn('Platform', 'Mid-level', '409 in CI', 'Schema rejected.', 'do?', '<ul><li>Read verbose messages.</li><li>Add defaults or redesign.</li></ul>', 'Set NONE.') +
    scn('Platform', 'Mid-level', 'Old consumer breaks', 'After producer deploy.', 'cause?', '<ul><li>Mode BACKWARD but producers upgraded first.</li><li>Use FULL or deploy consumers first.</li></ul>', 'Blame Kafka.') +
    scn('Data', 'Senior', 'Change units', 'Price rupees → paise.', 'plan?', '<ul><li>New field price_paise, migrate, deprecate.</li><li>Or new topic.</li></ul>', 'Change values silently.'))
