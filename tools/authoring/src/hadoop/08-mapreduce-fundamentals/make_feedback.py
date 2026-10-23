# make_feedback.py: create feedback.txt, 2 lakh short canteen feedback lines (same file every time)
import random
random.seed(11)
items = ["chai", "samosa", "vada pav", "poha", "idli", "dosa"]
good = ["tasty", "hot", "fresh", "crispy", "perfect", "good", "nice", "amazing"]
bad = ["cold", "late", "oily", "salty", "costly", "stale", "slow"]
starts = ["the", "today the", "my", "loved the", "please improve the", "why is the"]
with open("feedback.txt", "w") as f:
    for _ in range(200_000):
        item = random.choice(items)
        words = random.choice(good if random.random() < 0.7 else bad)
        f.write(f"{random.choice(starts)} {item} was {words}\n")
print(open("feedback.txt").read().count("\n"), "lines")
