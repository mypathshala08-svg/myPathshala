"""4.1 Segments: a small segment.bytes (1 MiB, the minimum) makes the log roll so we can see every file."""
import json, subprocess, time
from confluent_kafka import Producer
from common import BS, fresh
T = "seg-41"
print("== 0) try a 16 KB segment size")
try:
    fresh(T, 1, 3, {"segment.bytes": "16384"})
except Exception as e:
    print("  ", e.args[0].str())
fresh(T, 1, 3, {"segment.bytes": "1048576", "index.interval.bytes": "4096"})
def sh(cmd):
    return subprocess.run(["docker", "exec", "k1", "sh", "-c", cmd], capture_output=True, text=True).stdout.rstrip()
p = Producer({"bootstrap.servers": BS, "linger.ms": 0, "batch.num.messages": 10})
for i in range(10000):
    p.produce(T, key=f"o{i}", value=json.dumps({"order": f"o{i:04d}", "city": "Pune", "amount": 250, "status": "PLACED", "note": "x" * 200}))
    if i % 100 == 99: p.flush()
p.flush(); time.sleep(2)
print("== 1) the partition folder after 10,000 orders (segment.bytes=1 MiB)")
print(sh(f"cd /var/lib/kafka/data/{T}-0 && stat -c '%10s  %n' *"))
print("== 2) file names = base offset of the first record in that segment")
print(sh(f"cd /var/lib/kafka/data/{T}-0 && ls *.log"))
print("== 3) dump the start of the SECOND segment")
second = sh(f"cd /var/lib/kafka/data/{T}-0 && ls *.log | sed -n 2p")
print(f"  {second}:")
print(sh(f"/opt/kafka/bin/kafka-dump-log.sh --files /var/lib/kafka/data/{T}-0/{second} 2>/dev/null | grep -m2 baseOffset | sed -E 's/ (lastSequence|producerEpoch|partitionLeaderEpoch|isTransactional|isControl|deleteHorizonMs|CreateTime|magic|compresscodec|crc|isvalid|baseSequence|producerId): [^ ]*//g'"))
print("== 4) end offsets and log start")
print(sh(f"/opt/kafka/bin/kafka-get-offsets.sh --bootstrap-server k1:9092 --topic {T} --time -2; /opt/kafka/bin/kafka-get-offsets.sh --bootstrap-server k1:9092 --topic {T} --time -1"))
print("== 5) segment size on disk via kafka-log-dirs (one partition, three replicas)")
out = sh(f"/opt/kafka/bin/kafka-log-dirs.sh --bootstrap-server k1:9092 --describe --topic-list {T} 2>/dev/null | tail -1")
import re
print("  sizes per broker:", re.findall(r'"partition":"seg-41-0","size":(\d+)', out))
