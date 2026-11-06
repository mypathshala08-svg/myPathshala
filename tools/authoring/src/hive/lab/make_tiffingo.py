"""Synthetic TiffinGo datasets for the Apache Hive course (deterministic, seed 42).
usage: python3 make_tiffingo.py OUT_DIR"""
import csv, json, os, random, sys, datetime as dt
out = sys.argv[1] if len(sys.argv) > 1 else 'data'
os.makedirs(out, exist_ok=True)
R = random.Random(42)
CITIES = [('Mumbai', 'MH'), ('Pune', 'MH'), ('Thane', 'MH'), ('Navi Mumbai', 'MH'), ('Bengaluru', 'KA'), ('Hyderabad', 'TS'), ('Delhi', 'DL'), ('Chennai', 'TN')]
WEIGHTS = [22, 16, 9, 8, 18, 12, 10, 5]
FIRST = 'Aarav Aditi Arjun Ananya Diya Ishaan Kabir Kavya Meera Neha Nikhil Priya Rahul Riya Rohan Sanya Siddharth Sneha Tanvi Vihaan Zoya Farhan Gurpreet Joseph Lakshmi'.split()
LAST = 'Sharma Patil Iyer Reddy Khan Singh Nair Joshi Desai Kulkarni Gupta Mehta Rao Das Fernandes Pillai'.split()
CUISINE = ['North Indian', 'South Indian', 'Maharashtrian', 'Gujarati', 'Chinese', 'Bengali', 'Punjabi', 'Healthy']
DISHES = {'North Indian': ['Dal Makhani', 'Paneer Butter Masala', 'Roti', 'Jeera Rice'], 'South Indian': ['Idli', 'Masala Dosa', 'Sambar Rice', 'Curd Rice'],
          'Maharashtrian': ['Poha', 'Misal Pav', 'Varan Bhaat', 'Puran Poli'], 'Gujarati': ['Thepla', 'Dhokla', 'Gujarati Thali', 'Khichdi'],
          'Chinese': ['Veg Hakka Noodles', 'Manchurian', 'Fried Rice', 'Spring Roll'], 'Bengali': ['Fish Curry Rice', 'Luchi', 'Aloo Posto', 'Mishti Doi'],
          'Punjabi': ['Chole Bhature', 'Rajma Chawal', 'Lassi', 'Aloo Paratha'], 'Healthy': ['Millet Bowl', 'Sprouts Salad', 'Ragi Dosa', 'Fruit Bowl']}
PAY = ['UPI'] * 6 + ['Card'] * 2 + ['COD', 'Wallet']

def wcity():
    return R.choices(CITIES, WEIGHTS)[0]

# customers
cust = []
for i in range(1, 2001):
    c, s = wcity()
    nm = f'{R.choice(FIRST)} {R.choice(LAST)}'
    joined = dt.date(2023, 1, 1) + dt.timedelta(days=R.randint(0, 1000))
    cust.append([i, nm, c, s, joined.isoformat(), R.choice(['Gold', 'Silver', 'Basic', 'Basic'])])
with open(f'{out}/customers.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['customer_id', 'name', 'city', 'state', 'joined_on', 'plan']); w.writerows(cust)

# restaurants (kitchens)
rest = []
for i in range(1, 121):
    c, s = wcity(); cu = R.choice(CUISINE)
    rest.append(dict(restaurant_id=i, name=f'{R.choice(LAST)} {R.choice(["Kitchen", "Tiffins", "Bhojanalay", "Mess", "Foods"])}', city=c, cuisine=cu,
                     rating=round(R.uniform(3.2, 4.9), 1), tags=R.sample(['veg', 'jain', 'budget', 'premium', 'late-night', 'office-lunch'], R.randint(1, 3)),
                     contact={'phone': f'+91-00000-{i:05d}', 'email': f'kitchen{i}@tiffingo.in'}))
with open(f'{out}/restaurants.json', 'w') as f:
    for r in rest: f.write(json.dumps(r, ensure_ascii=False) + '\n')

# orders (CSV, no header, pipe-free; 50,000 rows over Oct 2026)
start = dt.datetime(2026, 10, 1)
by_city = {}
for r in rest: by_city.setdefault(r['city'], []).append(r)
orders, items = [], []
for oid in range(100001, 150001):
    cu = R.choice(cust); rs = R.choice(by_city.get(cu[2]) or rest)
    ts = start + dt.timedelta(minutes=R.randint(0, 30 * 24 * 60 - 1))
    n = R.randint(1, 4); dishes = R.sample(DISHES[rs['cuisine']], n)
    amt = sum(R.choice([40, 60, 80, 90, 120, 150, 180, 220]) for _ in dishes)
    st = R.choices(['DELIVERED', 'CANCELLED', 'REFUNDED'], [92, 6, 2])[0]
    orders.append([oid, cu[0], rs['restaurant_id'], cu[2], ts.strftime('%Y-%m-%d %H:%M:%S'), amt, R.choice(PAY), st])
    items.append((oid, dishes))
# a few dirty rows to teach schema-on-read
dirty = [[150001, 17, 3, 'Pune', '2026-10-31 21:15:00', 'abc', 'UPI', 'DELIVERED'],
         [150002, 18, 4, 'Mumbai', '31/10/2026 21:20', 210, 'UPI', 'DELIVERED']]
with open(f'{out}/orders.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerows(orders); w.writerows(dirty)
# order items as complex-type text: id|dish1,dish2|key:val;key:val
# order_items_v1.txt uses ';' between map entries (a delimiter mistake used in Lesson 2.3);
# order_items.txt is the fixed file with ',' for array items and map entries alike.
with open(f'{out}/order_items_v1.txt', 'w') as f1, open(f'{out}/order_items.txt', 'w') as f2:
    for oid, d in items[:5000]:
        sp, cu = R.choice(["mild", "medium", "hot"]), R.choice(["yes", "no"])
        f1.write(f'{oid}|{",".join(d)}|spice:{sp};cutlery:{cu}\n')
        f2.write(f'{oid}|{",".join(d)}|spice:{sp},cutlery:{cu}\n')
# web access log lines for RegexSerDe
with open(f'{out}/access.log', 'w') as f:
    for k in range(3000):
        ts = start + dt.timedelta(seconds=k * 37)
        ip = f'10.{R.randint(0,255)}.{R.randint(0,255)}.{R.randint(1,254)}'
        path = R.choice(['/menu', '/cart', '/checkout', '/track', '/api/orders', '/offers'])
        code = R.choices([200, 304, 404, 500], [85, 8, 5, 2])[0]
        f.write(f'{ip} - - [{ts.strftime("%d/%b/%Y:%H:%M:%S")} +0530] "GET {path} HTTP/1.1" {code} {R.randint(200, 9000)}\n')
print('customers', len(cust), 'restaurants', len(rest), 'orders', len(orders) + len(dirty))
