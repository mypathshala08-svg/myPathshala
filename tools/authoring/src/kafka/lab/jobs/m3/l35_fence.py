"""3.5b Zombie fencing: a second instance with the same transactional.id fences the first."""
from confluent_kafka import Producer, KafkaException
BS = "k1:9092"
old = Producer({"bootstrap.servers": BS, "transactional.id": "alert-writer"})
old.init_transactions(); old.begin_transaction(); old.produce("ledger-35", value="Z1 from old instance")
print("  old instance: transaction open, epoch assigned")
new = Producer({"bootstrap.servers": BS, "transactional.id": "alert-writer"})
new.init_transactions(); print("  new instance: init_transactions() -> epoch bumped, old transaction aborted")
try:
    old.commit_transaction(); print("  old instance commit: succeeded (unexpected)")
except KafkaException as e:
    print("  old instance commit:", e.args[0].str())
