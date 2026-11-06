"""5.3 Leader election: preferred leader election, and a leader crash measured from a producer's view."""
import subprocess, time, re
from confluent_kafka import Producer
def sh(c, node="k1"): return subprocess.run(["docker", "exec", node, "sh", "-c", c], capture_output=True, text=True).stdout.rstrip()
def desc(t, node="k1"):
    return "\n".join(re.sub(r"\tElr.*|\tTopicId: [^\t]*", "", l) for l in sh(f"/opt/kafka/bin/kafka-topics.sh --bootstrap-server {node}:9092 --describe --topic {t}", node).split("\n") if "Partition:" in l)
print("== 1) small-51 partition 0 after the reassignment in 5.1: replicas 3,1 but leader 1")
print(desc("small-51"))
print("== 2) preferred leader election (first replica in the list should lead)")
print(sh("/opt/kafka/bin/kafka-leader-election.sh --bootstrap-server k1:9092 --election-type PREFERRED --topic small-51 --partition 0"))
print(desc("small-51"))
print("== 3) kill the leader of rides-51 partition 0 while a producer keeps writing to it")
lead = re.search(r"Partition: 0\tLeader: (\d+)", desc("rides-51")).group(1)
print("  leader of P0 is broker", lead)
p = Producer({"bootstrap.servers": "k1:9092,k2:9092,k3:9092", "acks": "all", "linger.ms": 0})
log = []
def cb(err, m, sent):
    log.append((sent, time.time(), err is None))
t_kill = None
for i in range(160):
    now = time.time()
    p.produce("rides-51", value=f"gps-{i}", partition=0, callback=lambda e, m, s=now: cb(e, m, s))
    p.poll(0)
    if i == 40:
        subprocess.run(["docker", "kill", f"k{lead}"], capture_output=True); t_kill = time.time()
    time.sleep(0.1)
p.flush(30)
ok = sorted(t for s, t, good in log if good)
gap = max(b - a for a, b in zip(ok, ok[1:]))
after = [t for t in ok if t > t_kill]
print(f"  sent 160 records (10 per second), killed broker {lead} after 40")
print(f"  delivered: {sum(1 for *_, g in log if g)} of 160, failed: {sum(1 for *_, g in log if not g)}")
print(f"  first confirmation after the kill: +{after[0] - t_kill:.1f} s; longest gap between confirmations: {gap:.1f} s")
other = "2" if lead != "2" else "1"
print(desc("rides-51", f"k{other}").split("\n")[0])
subprocess.run(["docker", "start", f"k{lead}"], capture_output=True)
time.sleep(25)
print("== 4) broker back; automatic preferred-leader rebalancing restores leadership")
print("  auto.leader.rebalance.enable =", re.search(r"auto.leader.rebalance.enable=(\w+)", sh("/opt/kafka/bin/kafka-configs.sh --bootstrap-server k1:9092 --entity-type brokers --entity-name 1 --describe --all")).group(1))
print(desc("rides-51").split("\n")[0])
