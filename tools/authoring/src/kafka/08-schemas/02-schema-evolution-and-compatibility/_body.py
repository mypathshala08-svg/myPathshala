import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from kafkakit import *
C = 'l82_compat.txt'
def sec(a, b=None, drop=()):
    return capsec(C, a, b, drop)
B = '../../'
hk = hook('You add one new field to the Order schema and the registry answers HTTP 409. Add the same field with a default and it says 200. Why does one word matter so much?',
    'Because old and new programs read each other’s data. <b>Compatibility modes</b> (BACKWARD, FORWARD, FULL, NONE and their TRANSITIVE versions) decide which changes are safe for which side. We tested <b>6 real changes × 4 modes</b> against the registry and read real Avro bytes with old and new schemas to see exactly why each answer is yes or no.',
    ['What BACKWARD, FORWARD and FULL really protect.',
     'Which changes are safe: add/delete fields, defaults, renames, type changes.',
     'The deploy order each mode requires.'])
cmap = concept_map('Concept map. Beginner: schema version, old vs new program. Intermediate: reader and writer schema, defaults, compatibility modes. Advanced: transitive modes, type promotion, aliases for renames, deploy order, Protobuf field numbers.',
    [[('sv', 'Schema versions', 'Lesson 8.1', B + '08-schemas/01-schema-registry/'), ('rw', 'Writer vs reader', 'two schemas', None)],
     [('df', 'Defaults', 'fill missing', None), ('bw', 'BACKWARD', 'new reads old', None), ('fw', 'FORWARD', 'old reads new', None), ('fu', 'FULL', 'both', None)],
     [('tr', 'TRANSITIVE', 'all versions', None), ('tp', 'Type promotion', 'int → long', None), ('al', 'Aliases', 'renames', None), ('do', 'Deploy order', 'who first', None)]],
    [('sv', 'rw'), ('rw', 'df'), ('df', 'bw'), ('df', 'fw'), ('bw', 'fu'), ('fw', 'fu'), ('fu', 'tr'), ('bw', 'tp'), ('fu', 'al'), ('bw', 'do'), ('fw', 'do')],
    {'rw', 'df', 'bw', 'fw', 'fu', 'tr', 'tp', 'al', 'do'},
    '<b>Builds on:</b> <a href="../01-schema-registry/">8.1</a>. <b>Next:</b> Module 9 stream processing.')
whw = why_how_where(
    'Topics keep old messages for days or forever (compaction), and producers and consumers upgrade at different times. Every new schema must be readable alongside the old ones, or someone breaks.',
    'Avro decodes with two schemas: the <b>writer</b> schema (by id in the message) and the consumer’s <b>reader</b> schema. Fields are matched by name: missing fields in the data take the reader’s default; extra fields are skipped. The registry simulates this for every new version and refuses (409) incompatible ones.',
    'Every long-lived topic with more than one team; CDC topics when tables change; event-sourced systems that replay history.',
    'BACKWARD (default) only checks against the previous version; use *_TRANSITIVE if consumers may read very old data. Renames are never safe without aliases; changing meaning (price in rupees → paise) is “compatible” but still breaks people.')

def two_sch(hl, extra='+ spicy (default false)'):
    o = box(10, 34, 150, 74, 'blue' if hl != 0 else 'acc', rx=6) + t(85, 50, 'writer v1 (data)', 8, bold=True) + t(85, 68, 'id item qty price', 7.4, mono=True)
    o += box(196, 34, 150, 74, 'green' if hl != 1 else 'acc', rx=6) + t(271, 50, 'reader v2', 8, bold=True) + t(271, 68, 'id item qty price', 7.4, mono=True) + t(271, 84, extra, 7.2, mono=True)
    return o + arrow(162, 70, 194, 70) + t(178, 24, 'match by field name', 7.4)
scene_svg = scene('Avro schema resolution: data written with v1 (id, item, qty, price) is read with reader schema v2, which adds a field spicy with default false; the missing field is filled from the default.', two_sch(-1),
                  'Missing field + <tspan font-weight="700" class="s-acc">default</tspan> = old data still readable.')
dialogue = '''K> Sir, product wants a “spicy” flag on orders. I added the field and the registry rejected it with 409.
A> Your field had no default. New consumers reading <b>old</b> orders would find no spicy value and nothing to fill in. Under BACKWARD that is forbidden.
R> So defaults are the secret?
A> Mostly. But which changes are safe depends on who upgrades first. Let’s test six changes in four modes against the real registry.'''

lv = '''
LEVELS> Compatibility at three levels
L1> Old and new phone apps
      <ul>
        <li>BACKWARD: the new app can open files saved by the old app. FORWARD: the old app can open files saved by the new app (it ignores what it doesn’t understand). FULL: both. Upgrade order follows from that.</li>
      </ul>
L2> The modes
      <ul>
        <li><b>BACKWARD</b> (default): new schema reads data of the previous one. Allowed: delete fields, add fields <i>with defaults</i>. Upgrade <b>consumers first</b>.</li>
        <li><b>FORWARD</b>: previous schema reads data of the new one. Allowed: add fields, delete fields <i>that had defaults</i>. Upgrade <b>producers first</b>.</li>
        <li><b>FULL</b>: both directions: only add/delete fields that have defaults. Any order. <b>NONE</b>: no checks. <b>*_TRANSITIVE</b>: checked against all earlier versions, not just the last.</li>
      </ul>
L3> Details that bite
      <ul>
        <li>Avro <b>type promotion</b>: int → long/float/double, long → float/double, float → double, string ↔ bytes. So a reader can widen (BACKWARD OK) but an old int reader cannot read long data (FORWARD fails), as our matrix shows.</li>
        <li><b>Renames</b> break by-name matching; Avro <code>aliases</code> on the reader field can map an old name. Unions with <code>null</code> first and default <code>null</code> are the usual way to make optional fields.</li>
        <li><b>Protobuf</b>: fields are matched by number; never reuse or change a number, use <code>reserved</code>. <b>JSON Schema</b>: compatibility depends on open/closed content models (<code>additionalProperties</code>).</li>
        <li>Big breaking changes: create a new topic (orders-v2), dual-write or migrate with a stream job, then retire the old topic.</li>
      </ul>
/LEVELS
'''
MX = figure('Compatibility matrix from the lab for six changes against v1 in BACKWARD, FORWARD, FULL and NONE: add field with default allowed in all; add field without default allowed only in FORWARD and NONE; delete field price allowed in BACKWARD and NONE; rename allowed only in NONE; widen int to long allowed in BACKWARD and NONE; change double to string allowed only in NONE.',
    t(16, 20, 'Real registry answers (Y = accepted)', 8.6, 'ink', anchor='start', bold=True) +
    ''.join(t(250 + j * 70, 40, m, 7.6, bold=True) for j, m in enumerate(['BACKWARD', 'FORWARD', 'FULL', 'NONE'])) +
    ''.join(t(16, 62 + i * 20, n, 7.6, 'ink', anchor='start') + ''.join(box(226 + j * 70, 50 + i * 20, 48, 16, 'green' if c == 'Y' else 'red', rx=3) + t(250 + j * 70, 62 + i * 20, c, 7.6, bold=True) for j, c in enumerate(r))
            for i, (n, r) in enumerate([('add field WITH default', 'YYYY'), ('add field WITHOUT default', '-Y-Y'), ('delete field (no default)', 'Y--Y'),
                                        ('rename qty → quantity', '---Y'), ('widen int → long', 'Y--Y'), ('double → string', '---Y')])),
    h=200, caption='Only “add with default” is safe in every mode.')
extra = '''

  <h3>The matrix at a glance</h3>
''' + MX

types_html = table(['Mode', 'Checks', 'Safe changes', 'Upgrade first'], [
    ['BACKWARD (default)', 'new reads previous', 'delete field; add field with default', 'consumers'],
    ['BACKWARD_TRANSITIVE', 'new reads all previous', 'same', 'consumers'],
    ['FORWARD', 'previous reads new', 'add field; delete field with default', 'producers'],
    ['FORWARD_TRANSITIVE', 'all previous read new', 'same', 'producers'],
    ['FULL / FULL_TRANSITIVE', 'both directions', 'add/delete fields with defaults', 'any order'],
    ['NONE', 'nothing', 'anything (risky)', 'coordinate manually'],
], minw=660)
warn = 'BACKWARD checks only against the latest version. If a consumer can re-read a topic from the start (compacted or long retention), v3 may be compatible with v2 but not with v1. Use BACKWARD_TRANSITIVE or FULL_TRANSITIVE for such topics.'

steps = [
    ('Step 1 · The 409',
     code('bash', 'terminal', 'curl -X POST localhost:8081/subjects/menu-82-value/versions \\\n  -H "Content-Type: application/vnd.schemaregistry.v1+json" -d \'{"schema": "<v1 + city:string>"}\'', sec('== 1)', '== 2)')),
     'Under BACKWARD, a new reader would find no city in old data and has no default: error READER_FIELD_MISSING_DEFAULT_VALUE.'),
    ('Step 2 · With a default',
     code('json', 'field', '{"name": "spicy", "type": "boolean", "default": false}', sec('== 2)', '== 3)')),
     'Accepted as version 2 of the subject (with a new global id).'),
    ('Step 3 · Six changes × four modes',
     code('bash', 'terminal', 'PUT  /config/{subject}   {"compatibility": "FORWARD"}\nPOST /compatibility/subjects/{subject}/versions/latest?verbose=true', sec('== 3)', '== 4)')),
     'Only adding a field with a default passes everywhere. Deleting a field or widening int → long is fine for new readers (BACKWARD) but breaks old readers (FORWARD). Renames and real type changes fail in every checked mode.'),
    ('Step 4 · Why, on real bytes',
     code('python', 'l82.py', 'fastavro.schemaless_reader(io.BytesIO(data), writer_schema, reader_schema)', sec('== 4)', '== 5)')),
     'New reader on old data: <code>spicy</code> filled with False. Old reader on new data: <code>spicy</code> skipped. A reader with a field without default fails with SchemaResolutionError: the exact reason for the 409.'),
    ('Step 5 · Other formats',
     code('bash', 'terminal', 'POST /subjects/riders-82-value/versions {"schemaType": "PROTOBUF", "schema": "syntax = \\"proto3\\"; ..."}', sec('== 5)')),
     'The same registry stores Protobuf and JSON Schema with their own compatibility rules.'),
]
see = [term([('HTTP 409', RD), ('READER_FIELD_MISSING_', Y), ('DEFAULT_VALUE', Y)], size=7.0), term([('HTTP 200 version 2', G)], size=7.4),
       term([('with default: Y Y Y Y', G), ('rename:      - - - Y', RD)], size=7.0), term([("spicy: False (filled)", G), ('spicy skipped by v1', W)], size=7.0),
       term([('PROTOBUF id 4', W), ('JSON id 5', W)], size=7.2)]
B1 = [two_sch(1, '+ city (NO default)'), two_sch(1), two_sch(-1), two_sch(0), two_sch(-1)]
B1 = [b + cap(c, '', tn, y=124, h=30) for b, c, tn in zip(B1, ['No default → refused', 'Default → accepted', 'Matrix checked', 'Resolution on bytes', 'Any format'], ['red', 'green', 'blue', 'green', 'violet'])]
two = anim_two('Schema evolution', '409, matrix, bytes', 'Real outputs from the lab', 'Reader meets writer', see, B1, ['Refuse.', 'Accept.', 'Matrix.', 'Bytes.', 'Formats.'], ['409.', 'v2.', 'Rules.', 'Why.', 'Proto/JSON.'])
pe = peel('A new version, layer by layer', 'Registering v2 with spicy. (Simplified.)',
    [('POST', ''), ('Mode', ''), ('Simulate', ''), ('Decide', ''), ('Store', ''), ('Use', '')],
    [['POST', 'new schema', 'subject menu-82-value', ''], ['Mode', 'BACKWARD', 'compare with latest', ''], ['Simulate', 'reader = new', 'writer = v1', 'field spicy missing'],
     ['Decide', 'default exists', '→ compatible', ''], ['Store', 'version 2', '_schemas topic', 'new id'], ['Use', 'producers write v2', 'old data still readable', '']],
    ['Submit.', 'Mode.', 'Simulate.', 'Decide.', 'Store.', 'Use.'], 'scenario-peel')
scen = five('Real-time scenario 1', 'Adding a field safely', 'Spicy flag. (Typical.)', ('BACKWARD + default', 'Consumers first'), [
    ('Add spicy with default', 'registry OK', 'v2.', 'green'), ('Deploy consumers', 'reader v2', 'Old data fine.', 'green'),
    ('Deploy producers', 'write v2', 'New data.', 'green'), ('Old consumer still around?', 'it skips spicy only if FORWARD-safe', 'Check.', 'amber'),
    ('Use FULL for shared topics', 'any order', 'Simple.', 'blue')], ['Add.', 'Readers.', 'Writers.', 'Check.', 'FULL.'], 'scenario-add') + \
       five('Real-time scenario 2', 'Rename a field', 'qty → quantity. (Typical.)', ('Renames', 'Add new, migrate, remove old'), [
    ('Direct rename', 'rejected', 'All modes.', 'red'), ('Add quantity with default', 'keep qty', 'Compatible.', 'green'),
    ('Producers fill both', 'transition', 'Dual.', 'amber'), ('Consumers move to quantity', 'over weeks', 'Migrate.', 'green'),
    ('Delete qty (had default)', 'FULL-safe', 'Done.', 'blue')], ['Fail.', 'Add.', 'Both.', 'Move.', 'Remove.'], 'scenario-rename') + \
       five('Real-time scenario 3 · advanced', 'Breaking change needed', 'price double → string. (Typical.)', ('New topic', 'Do not fight the rules'), [
    ('Type change refused', 'every mode', 'By design.', 'red'), ('Create orders-v2', 'new subject', 'Clean.', 'green'),
    ('Stream job converts', 'v1 → v2', 'Bridge.', 'green'), ('Consumers switch', 'one by one', 'Migrate.', 'amber'),
    ('Retire orders-v1', 'after retention', 'Done.', 'blue')], ['Refuse.', 'Topic.', 'Convert.', 'Switch.', 'Retire.'], 'scenario-break')
assemble(HERE, h2_story='Changing a schema without breaking anyone', hook_html=hk,
    narration='Product wants a new “spicy” flag on TiffinGo orders. Ten consumers read the orders topic, some updated weekly, some yearly. Kabir must change the schema without breaking any of them.',
    scene_svg=scene_svg, dialogue=dialogue, def_h2='Schema evolution and compatibility',
    formal='<b>Schema evolution</b> is changing a schema over time while existing data and programs keep working. A registry <b>compatibility mode</b> defines the allowed relation between versions: <b>BACKWARD</b> (consumers using the new schema can read data written with the previous one), <b>FORWARD</b> (consumers using the previous schema can read data written with the new one), <b>FULL</b> (both), each optionally <b>TRANSITIVE</b> (against all earlier versions), or <b>NONE</b>. Avro achieves this by resolving writer and reader schemas by field name, using reader defaults for missing fields.',
    simple='Every change to a message shape must still let old and new programs read each other’s messages. Adding a field with a default value is almost always safe; renaming or changing a type is not.',
    term_rows=[('Writer schema', 'Used to write the data.'), ('Reader schema', 'Used by the consumer.'), ('Default', 'Value for missing field.'), ('BACKWARD', 'New reads old.'), ('FORWARD', 'Old reads new.'), ('FULL', 'Both.'), ('TRANSITIVE', 'Against all versions.'), ('Alias', 'Old name for a field.')],
    whw=whw, cmap=cmap, extra_def=extra, lv=lv,
    myth_rows=[('Adding a field is always safe.', 'Not without a default under BACKWARD.', 'Step 1: 409.'),
               ('Widening int → long is safe everywhere.', 'Old int readers fail: FORWARD no.', 'Matrix.'),
               ('Compatible means meaning is unchanged.', 'Registry checks types, not semantics.', 'Scenario 3.')],
    exam='“Explain schema compatibility.” BACKWARD: new reader reads old data (add with default, delete), consumers first; FORWARD: old reader reads new (add, delete with default), producers first; FULL both; TRANSITIVE all versions; renames/type changes break; Avro resolves by name with defaults.',
    types_h2='Modes and deploy order', types_html=types_html, warn=warn,
    steps_h2='Test the rules', steps_intro='All outputs are real: Confluent Schema Registry 8.1.0 REST API and fastavro schema resolution.',
    steps=steps, two=two, peel_intro='Now peel one registration.', peel_html=pe,
    scen_intro='Three live scenarios: adding, renaming, and a breaking change.', scen=scen,
    uc_h2='Evolution at work', ucs=[uc_('add', 'grow', 'green', '1. New optional fields', 'The everyday change.', ['v1', '*default', 'v2']),
        uc_('ci', 'CI', 'blue', '2. CI compatibility checks', 'Fail the build, not production.', ['PR', '*check', 'Merge']),
        uc_('cdc', 'CDC', 'violet', '3. Table changes in CDC', 'ALTER TABLE flows as new versions.', ['DDL', '*registry', 'Topic']),
        uc_('mig', 'migrate', 'amber', '4. Breaking migrations', 'New topic + converter job.', ['v1', '*bridge', 'v2'])],
    uc_note='Examples are simplified descriptions of common practice.',
    pre='<b>Before you start:</b> <a href="../01-schema-registry/">8.1 Schema Registry</a>.')
