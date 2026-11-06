"""Deterministic TiffinGo customer reviews (3 files, one per month)."""
import random, os
R = random.Random(2026)
dishes = ["poha", "misal pav", "masala dosa", "idli", "dal makhani", "paneer butter masala", "chole bhature", "biryani", "thepla", "fried rice"]
good = ["tasty", "hot", "fresh", "quick delivery", "great packing", "loved it", "value for money"]
bad = ["cold", "late", "too spicy", "less quantity", "spilled", "oily", "missing items"]
os.makedirs("data/tiffingo/reviews", exist_ok=True)
for m, n in (("2026-08", 7000), ("2026-09", 8000), ("2026-10", 9000)):
    with open(f"data/tiffingo/reviews/reviews_{m}.txt", "w") as f:
        for i in range(n):
            d = R.choice(dishes); words = R.sample(good if R.random() < 0.7 else bad, 2)
            f.write(f"{d} was {words[0]} and {words[1]}\n")
