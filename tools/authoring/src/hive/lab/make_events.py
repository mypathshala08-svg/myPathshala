"""Deterministic TiffinGo app events (JSON lines) for Lesson 4.3. One malformed line on purpose."""
import json, random
random.seed(43)
cities = ['Mumbai', 'Pune', 'Thane', 'Bengaluru', 'Hyderabad', 'Chennai', 'Delhi']
dishes = {'Idli': 60, 'Masala Dosa': 90, 'Poha': 45, 'Misal Pav': 80, 'Chai': 20, 'Lassi': 50, 'Veg Thali': 150, 'Rajma Chawal': 120}
events = ['app_open', 'search', 'order_placed', 'order_placed', 'coupon_applied']
out = []
for i in range(1, 2001):
    ev = random.choice(events)
    d = {'event': ev, 'ts': f'2026-10-{1 + i % 7:02d}T{8 + i % 14:02d}:{i % 60:02d}:00+05:30',
         'user': {'id': random.randint(1, 2000), 'city': random.choice(cities)},
         'device': {'os': random.choice(['Android', 'Android', 'iOS']), 'app_ver': random.choice(['5.2.0', '5.3.1'])}}
    if ev == 'order_placed':
        ks = random.sample(list(dishes), random.randint(1, 3))
        d['items'] = [{'dish': k, 'qty': random.randint(1, 3), 'price': dishes[k]} for k in ks]
    if ev == 'coupon_applied':
        d['coupon'] = random.choice(['WELCOME50', 'DIWALI20', None])
    if ev == 'search':
        d['query'] = random.choice(['dosa', 'thali', 'poha near me', 'chai'])
    out.append(json.dumps(d, separators=(',', ':')))
out[1499] = out[1499][:-15]          # one truncated line, as happens with partial uploads
open('/home/claude/lab/hive/data/events/app_events.json', 'w').write('\n'.join(out) + '\n')
print(len(out), 'lines')
