"""4.2 How a read finds offset 5000: segment by file name, then the sparse .index, then a short scan."""
import subprocess, bisect, time
from confluent_kafka import Consumer, TopicPartition
T, D = "seg-41", "/var/lib/kafka/data/seg-41-0"
def sh(cmd):
    return subprocess.run(["docker", "exec", "k1", "sh", "-c", cmd], capture_output=True, text=True).stdout.rstrip()
segs = sh(f"cd {D} && ls *.log").split()
bases = [int(s.split(".")[0]) for s in segs]
target = 5000
seg = bases[bisect.bisect_right(bases, target) - 1]
print("== 1) step 1: pick the segment whose base offset is the largest <= 5000")
print("  segments:", bases, "-> segment", seg)
name = f"{seg:020d}"
print("== 2) step 2: the sparse offset index of that segment (first 6 of", sh(f"/opt/kafka/bin/kafka-dump-log.sh --files {D}/{name}.index 2>/dev/null | grep -c '^offset'"), "entries)")
idx = sh(f"/opt/kafka/bin/kafka-dump-log.sh --files {D}/{name}.index 2>/dev/null | grep '^offset'").split("\n")
print("\n".join("  " + l for l in idx[:6]))
pairs = [(int(l.split()[1]), int(l.split()[3])) for l in idx]
floor = max(p for p in pairs if p[0] <= target)
print(f"== 3) floor entry for 5000: offset {floor[0]} -> byte position {floor[1]}; scan forward from there")
batches = sh(f"/opt/kafka/bin/kafka-dump-log.sh --files {D}/{name}.log 2>/dev/null | grep baseOffset").split("\n")
hit = [b for b in batches if f"position: {floor[1]} " in b or int(b.split("baseOffset: ")[1].split()[0]) <= target <= int(b.split("lastOffset: ")[1].split()[0])]
for b in hit[:2]:
    print("  " + " ".join(x for x in b.split("  ") if x)[:0] + "baseOffset " + b.split("baseOffset: ")[1].split()[0] + "  lastOffset " + b.split("lastOffset: ")[1].split()[0] + "  position " + b.split("position: ")[1].split()[0])
print("== 4) the time index: timestamp -> offset (first 4 entries)")
print("\n".join("  " + l for l in sh(f"/opt/kafka/bin/kafka-dump-log.sh --files {D}/{name}.timeindex 2>/dev/null | grep '^timestamp'").split("\n")[:4]))
print("== 5) a consumer asks for offset 5000 directly")
c = Consumer({"bootstrap.servers": "k1:9092", "group.id": "idx-42"})
c.assign([TopicPartition(T, 0, 5000)])
m = None; t0 = time.time()
while m is None and time.time() - t0 < 10: m = c.poll(1.0)
print("  got offset", m.offset(), "value", m.value()[:40].decode(), "...")
c.close()
