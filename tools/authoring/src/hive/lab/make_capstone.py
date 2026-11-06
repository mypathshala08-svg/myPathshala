"""TiffinGo capstone landing data (Module 12). Deterministic, seed 2026.
usage: python3 make_capstone.py OUT_DIR
Writes one folder per daily load, the way a source system drops files:
  landing/orders/load_date=D/orders_D.csv        new orders + late arrivals + resends + status updates + dirty rows
  landing/customers/load_date=D/customers_D.csv  day 1 full snapshot, then only changes (CDC)
  landing/deliveries/load_date=D/events_D.json   rider events (JSON lines)
  landing/restaurants/restaurants.json           reference data
"""
import csv, json, os, random, sys, datetime as dt
OUT = sys.argv[1] if len(sys.argv) > 1 else 'data/capstone'
R = random.Random(2026)
D0, DAYS = dt.date(2026, 10, 1), 31
CITIES = ['Mumbai', 'Pune', 'Navi Mumbai', 'Thane', 'Bengaluru', 'Hyderabad']
CW = [26, 18, 10, 8, 24, 14]
FIRST = 'Aarav Aditi Arjun Ananya Diya Ishaan Kabir Kavya Meera Neha Nikhil Priya Rahul Riya Rohan Sanya Sneha Tanvi Vihaan Zoya Farhan Joseph Lakshmi'.split()
LAST = 'Sharma Patil Iyer Reddy Khan Singh Nair Joshi Desai Kulkarni Gupta Mehta Rao Das Pillai'.split()
CUISINE = ['North Indian', 'South Indian', 'Maharashtrian', 'Gujarati', 'Chinese', 'Healthy']
PAY = ['UPI'] * 13 + ['Card'] * 4 + ['COD'] * 2 + ['Wallet']
PLAN = ['Basic', 'Silver', 'Gold']


def ts(d, minute):
    return (dt.datetime.combine(d, dt.time()) + dt.timedelta(minutes=minute)).strftime('%Y-%m-%d %H:%M:%S')


def folder(kind, d):
    p = os.path.join(OUT, 'landing', kind, f'load_date={d.isoformat()}')
    os.makedirs(p, exist_ok=True)
    return p

# ---------------------------------------------------------------- reference: restaurants
rest = []
for i in range(1, 151):
    c = R.choices(CITIES, CW)[0]
    rest.append(dict(restaurant_id=i, name=f'{R.choice(LAST)} {R.choice(["Kitchen", "Tiffins", "Mess", "Foods", "Bhojanalay"])}',
                     city=c, cuisine=R.choice(CUISINE), rating=round(R.uniform(3.3, 4.9), 1),
                     tags=R.sample(['veg', 'jain', 'budget', 'premium', 'office-lunch', 'late-night'], R.randint(1, 3)),
                     onboarded=(dt.date(2024, 1, 1) + dt.timedelta(days=R.randint(0, 600))).isoformat()))
os.makedirs(os.path.join(OUT, 'landing', 'restaurants'), exist_ok=True)
with open(os.path.join(OUT, 'landing', 'restaurants', 'restaurants.json'), 'w') as f:
    for r in rest:
        f.write(json.dumps(r) + '\n')
by_city = {}
for r in rest:
    by_city.setdefault(r['city'], []).append(r['restaurant_id'])

# ---------------------------------------------------------------- customers (state + CDC)
cust = {}
for i in range(1, 3001):
    cust[i] = dict(customer_id=i, name=f'{R.choice(FIRST)} {R.choice(LAST)}', city=R.choices(CITIES, CW)[0],
                   plan=R.choices(PLAN, [60, 28, 12])[0], updated_at='2026-09-30 23:00:00')
HDR_C = ['customer_id', 'name', 'city', 'plan', 'updated_at']
next_cid = 3001

# ---------------------------------------------------------------- orders
HDR_O = ['order_id', 'customer_id', 'restaurant_id', 'order_ts', 'amount', 'payment', 'status', 'updated_at']
next_oid = 5_000_001
late_q = {}        # load day -> rows that arrive late
updates_q = {}     # load day -> refund updates
sent = {}          # order_id -> last row (for resends)
delivered_on = {}  # order_id -> (date, minute)
stats = dict(new=0, late=0, dup=0, resend=0, update=0, dirty=0, cust_changes=0, events=0)

for k in range(DAYS):
    d = D0 + dt.timedelta(days=k)
    # ---- customers file for this load
    rows_c = []
    if k == 0:
        rows_c = [dict(c) for c in cust.values()]
    else:
        for _ in range(R.randint(12, 22)):          # changes: a move or a plan change
            c = cust[R.randint(1, next_cid - 1)]
            if R.random() < 0.45:
                c['city'] = R.choice([x for x in CITIES if x != c['city']])
            else:
                c['plan'] = R.choice([p for p in PLAN if p != c['plan']])
            c['updated_at'] = ts(d - dt.timedelta(days=1), R.randint(600, 1380))
            rows_c.append(dict(c))
        for _ in range(R.randint(15, 30)):          # new sign-ups
            c = dict(customer_id=next_cid, name=f'{R.choice(FIRST)} {R.choice(LAST)}', city=R.choices(CITIES, CW)[0],
                     plan='Basic', updated_at=ts(d - dt.timedelta(days=1), R.randint(480, 1400)))
            cust[next_cid] = c; next_cid += 1
            rows_c.append(dict(c))
        stats['cust_changes'] += len(rows_c)
    with open(os.path.join(folder('customers', d), f'customers_{d:%Y%m%d}.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, HDR_C); w.writeheader(); w.writerows(rows_c)

    # ---- orders placed on business day d-1 are loaded on day d (nightly batch), first load = Oct 1 orders on Oct 2
    # keep it simple: load day d carries orders placed on day d (batch runs at 23:59)
    out, events = [], []
    weekend = d.weekday() >= 5
    n = R.randint(1350, 1550) + (250 if weekend else 0)
    for _ in range(n):
        c = cust[R.randint(1, next_cid - 1)]
        rid = R.choice(by_city[c['city']])
        minute = R.choices([R.randint(420, 600), R.randint(690, 900), R.randint(1140, 1380), R.randint(0, 1439)], [15, 40, 35, 10])[0]
        amt = sum(R.choice([60, 80, 90, 110, 120, 150, 180, 220, 260]) for _ in range(R.randint(1, 4)))
        st = R.choices(['DELIVERED', 'CANCELLED'], [93, 7])[0]
        row = dict(order_id=next_oid, customer_id=c['customer_id'], restaurant_id=rid, order_ts=ts(d, minute),
                   amount=f'{amt:.2f}', payment=R.choice(PAY), status=st, updated_at=ts(d, min(minute + 55, 1439)))
        next_oid += 1
        if st == 'DELIVERED':
            pick = minute + R.randint(8, 25)
            drop = pick + max(6, int(R.gauss(24 if c['city'] in ('Mumbai', 'Bengaluru') else 18, 7)))
            rider = R.randint(1, 400)
            events.append(dict(order_id=row['order_id'], event='PICKED_UP', event_ts=ts(d, pick), rider_id=rider))
            events.append(dict(order_id=row['order_id'], event='DELIVERED', event_ts=ts(d, drop), rider_id=rider))
            if R.random() < 0.015:                    # refunded 1-4 days later
                lag = R.randint(1, 4)
                u = dict(row, status='REFUNDED', updated_at=ts(d + dt.timedelta(days=lag), R.randint(540, 1260)))
                updates_q.setdefault(k + lag, []).append(u)
        if minute > 1380 and R.random() < 0.5 or R.random() < 0.02:   # late arrival: next load (or the one after)
            late_q.setdefault(k + R.choice([1, 1, 1, 2]), []).append(row)
        else:
            out.append(row); stats['new'] += 1
        sent[row['order_id']] = row
    for row in late_q.pop(k, []):
        out.append(row); stats['late'] += 1
    for row in updates_q.pop(k, []):
        out.append(row); stats['update'] += 1
    # resends: the source re-sends some rows of yesterday unchanged
    if k > 0:
        prev = [r for r in sent.values() if r['order_ts'][:10] == (d - dt.timedelta(days=1)).isoformat()]
        for row in R.sample(prev, 12):
            out.append(dict(row)); stats['resend'] += 1
    for row in R.sample(out, 6):                      # exact duplicate lines in the same file
        out.append(dict(row)); stats['dup'] += 1
    # dirty rows
    bad = [dict(order_id=next_oid + 900000 + k * 10, customer_id=R.randint(1, 3000), restaurant_id=999, order_ts=ts(d, 700), amount='240.00', payment='UPI', status='DELIVERED', updated_at=ts(d, 760)),
           dict(order_id=next_oid + 900001 + k * 10, customer_id=R.randint(1, 3000), restaurant_id=7, order_ts=ts(d, 710), amount='NA', payment='UPI', status='DELIVERED', updated_at=ts(d, 770)),
           dict(order_id=next_oid + 900002 + k * 10, customer_id='', restaurant_id=9, order_ts=ts(d, 720), amount='180.00', payment='Card', status='DELIVERED', updated_at=ts(d, 780))]
    if k % 3 == 0:
        bad.append(dict(order_id=next_oid + 900003 + k * 10, customer_id=R.randint(1, 3000), restaurant_id=11, order_ts=d.strftime('%d/%m/%Y') + ' 12:05', amount='150.00', payment='UPI', status='DELIVERED', updated_at=ts(d, 800)))
    if k % 4 == 1:
        bad.append(dict(order_id=next_oid + 900004 + k * 10, customer_id=R.randint(1, 3000), restaurant_id=12, order_ts=ts(d, 820), amount='-90.00', payment='UPI', status='DELIVERED', updated_at=ts(d, 830)))
    out += bad; stats['dirty'] += len(bad)
    R.shuffle(out)
    with open(os.path.join(folder('orders', d), f'orders_{d:%Y%m%d}.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, HDR_O); w.writeheader(); w.writerows(out)
    with open(os.path.join(folder('deliveries', d), f'events_{d:%Y%m%d}.json'), 'w') as f:
        for e in events:
            f.write(json.dumps(e) + '\n')
    stats['events'] += len(events)

print(json.dumps(stats), 'customers', next_cid - 1, 'last order id', next_oid - 1, 'left in queues', sum(map(len, late_q.values())), sum(map(len, updates_q.values())))
