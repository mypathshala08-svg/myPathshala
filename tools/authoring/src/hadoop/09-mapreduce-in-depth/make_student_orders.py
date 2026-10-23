# make_student_orders.py: 5 lakh canteen orders by 2,000 students over 30 days (same file every time)
# Columns: order_id,student_id,time,item,amount      plus menu.csv: item,category,counter
import random
from datetime import datetime, timedelta
random.seed(21)
menu = {"chai": ("drink", 15, "A"), "coffee": ("drink", 20, "A"), "samosa": ("snack", 18, "B"),
        "vada pav": ("snack", 20, "B"), "poha": ("breakfast", 25, "C"), "idli": ("breakfast", 30, "C"),
        "dosa": ("meal", 45, "D"), "thali": ("meal", 80, "D")}
weights = [30, 8, 14, 14, 9, 9, 10, 6]                      # chai is by far the most ordered
items = list(menu)
students = [f"S{n:04d}" for n in range(1, 2001)]
heavy = students[:20]                                        # 20 students who practically live in the canteen
start = datetime(2026, 9, 1)
hours = list(range(8, 21))                                   # canteen open 08:00 to 20:59
hour_w = [9, 7, 4, 4, 5, 9, 10, 6, 4, 6, 8, 5, 3]          # rush at breakfast, lunch and evening tea
with open("student_orders.csv", "w") as f:
    for oid in range(1, 500_001):
        sid = random.choice(heavy) if random.random() < 0.15 else random.choice(students)
        t = start + timedelta(days=random.randrange(30), hours=random.choices(hours, hour_w)[0], minutes=random.randrange(60))
        item = random.choices(items, weights)[0]
        f.write(f"{oid},{sid},{t:%Y-%m-%d %H:%M},{item},{menu[item][1]}\n")
with open("menu.csv", "w") as f:
    for item, (cat, price, counter) in menu.items():
        f.write(f"{item},{cat},{price},{counter}\n")
print("student_orders.csv: 500,000 orders; menu.csv:", len(menu), "items")
