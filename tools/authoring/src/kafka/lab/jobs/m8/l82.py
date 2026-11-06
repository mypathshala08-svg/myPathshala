import json, io, time, requests, fastavro
SR = 'http://localhost:8081'; H = {'Content-Type': 'application/vnd.schemaregistry.v1+json'}
def rec(fields): return {"type": "record", "name": "Order", "namespace": "in.tiffingo", "fields": fields}
F = lambda n, t, **k: {"name": n, "type": t, **k}
v1 = rec([F('id', 'int'), F('item', 'string'), F('qty', 'int'), F('price', 'double')])
changes = {
 'add field WITH default (spicy=false)': rec(v1['fields'] + [F('spicy', 'boolean', default=False)]),
 'add field WITHOUT default (city)':     rec(v1['fields'] + [F('city', 'string')]),
 'delete field price (no default)':      rec(v1['fields'][:3]),
 'rename qty -> quantity':               rec([v1['fields'][0], v1['fields'][1], F('quantity', 'int'), v1['fields'][3]]),
 'widen qty int -> long':                rec([v1['fields'][0], v1['fields'][1], F('qty', 'long'), v1['fields'][3]]),
 'change price double -> string':        rec(v1['fields'][:3] + [F('price', 'string')]),
}
def reset(subj, mode):
    requests.delete(f'{SR}/subjects/{subj}'); requests.delete(f'{SR}/subjects/{subj}?permanent=true')
    requests.put(f'{SR}/config/{subj}', headers=H, json={'compatibility': mode})
    return requests.post(f'{SR}/subjects/{subj}/versions', headers=H, json={'schema': json.dumps(v1)}).json()['id']
def check(subj, sch):
    r = requests.post(f'{SR}/compatibility/subjects/{subj}/versions/latest?verbose=true', headers=H, json={'schema': json.dumps(sch)}).json()
    return r.get('is_compatible'), r.get('messages', [])
print('== 1) register v1, then try a v2 that adds a field WITHOUT a default (BACKWARD)')
reset('menu-82-value', 'BACKWARD')
r = requests.post(f'{SR}/subjects/menu-82-value/versions', headers=H, json={'schema': json.dumps(changes['add field WITHOUT default (city)'])})
print('  HTTP', r.status_code, json.dumps(r.json())[:260])
print('== 2) the same subject, a v2 WITH a default: accepted')
r = requests.post(f'{SR}/subjects/menu-82-value/versions', headers=H, json={'schema': json.dumps(changes['add field WITH default (spicy=false)'])})
j = r.json(); print('  HTTP', r.status_code, {k: j[k] for k in ('id', 'version', 'schemaType')}, '-> versions', requests.get(f'{SR}/subjects/menu-82-value/versions').json())
print('== 3) compatibility matrix: each change checked against v1 in each mode (Y = allowed)')
modes = ['BACKWARD', 'FORWARD', 'FULL', 'NONE']
print('  ' + 'change'.ljust(40) + ''.join(m.ljust(10) for m in modes))
for name, sch in changes.items():
    row = []
    for m in modes:
        subj = f'mx-{m.lower()}-value'; reset(subj, m); ok, _ = check(subj, sch); row.append('Y' if ok else '-')
    print('  ' + name.ljust(40) + ''.join(x.ljust(10) for x in row))
print('== 4) why: old and new readers on real Avro bytes (fastavro schema resolution)')
v2 = changes['add field WITH default (spicy=false)']
def write(sch, r): b = io.BytesIO(); fastavro.schemaless_writer(b, fastavro.parse_schema(sch), r); return b.getvalue()
def read(b, w, r): return fastavro.schemaless_reader(io.BytesIO(b), fastavro.parse_schema(w), fastavro.parse_schema(r))
old = write(v1, {"id": 1, "item": "idli", "qty": 2, "price": 40.0})
new = write(v2, {"id": 9, "item": "vada", "qty": 3, "price": 60.0, "spicy": True})
print('  new reader (v2) on old data (v1):', read(old, v1, v2), '  <- default filled: BACKWARD')
print('  old reader (v1) on new data (v2):', read(new, v2, v1), '  <- extra field ignored: FORWARD')
nodef = changes['add field WITHOUT default (city)']
try: read(old, v1, nodef)
except Exception as e: print('  reader without default on old data:', type(e).__name__, str(e)[:90])
print('== 5) other formats: Protobuf and JSON Schema in the same registry')
proto = 'syntax = "proto3"; package tiffingo; message Rider { int32 id = 1; string name = 2; }'
js = json.dumps({"type": "object", "properties": {"id": {"type": "integer"}, "zone": {"type": "string"}}, "required": ["id"]})
for subj, typ, sch in [('riders-82-value', 'PROTOBUF', proto), ('zones-82-value', 'JSON', js)]:
    requests.delete(f'{SR}/subjects/{subj}'); requests.delete(f'{SR}/subjects/{subj}?permanent=true')
    r = requests.post(f'{SR}/subjects/{subj}/versions', headers=H, json={'schema': sch, 'schemaType': typ}).json()
    print(f'  {subj:16s} {typ:9s} -> id {r.get("id")}')
print('  GET /schemas/types ->', requests.get(SR + '/schemas/types').json())
