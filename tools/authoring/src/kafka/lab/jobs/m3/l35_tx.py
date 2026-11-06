"""3.5 Transactions: commit vs abort, read_committed vs read_uncommitted, control markers, EOS pipeline."""
import time, subprocess
from confluent_kafka import Producer, Consumer
from common import BS, fresh
T = "ledger-35"
fresh(T, 1)
p = Producer({"bootstrap.servers": BS, "transactional.id": "ledger-writer-1"})
p.init_transactions()
print("== 1) transaction A: 3 entries, committed")
p.begin_transaction()
for i in (1, 2, 3): p.produce(T, value=f"A{i} debit wallet Rs 100")
p.commit_transaction(); print("  committed")
print("== 2) transaction B: 2 entries, aborted (e.g. payment gateway said no)")
p.begin_transaction()
for i in (1, 2): p.produce(T, value=f"B{i} debit wallet Rs 5000")
p.flush(); p.abort_transaction(); print("  aborted")
print("== 3) transaction C: 1 entry, committed")
p.begin_transaction(); p.produce(T, value="C1 refund Rs 100"); p.commit_transaction(); print("  committed")
def read(iso):
    c = Consumer({"bootstrap.servers": BS, "group.id": f"r-{iso}-{time.time()}", "auto.offset.reset": "earliest", "isolation.level": iso})
    c.subscribe([T]); out, idle = [], 0
    while idle < 5:
        m = c.poll(1.0)
        if m is None: idle += 1; continue
        if not m.error(): out.append((m.offset(), m.value().decode()[:2]))
    c.close(); return out
print("== 4) what consumers see")
print("  read_uncommitted:", read("read_uncommitted"))
print("  read_committed  :", read("read_committed"))
print("== 5) on disk: data batches and control (marker) batches")
print(subprocess.run(["docker", "exec", "k1", "sh", "-c", f"/opt/kafka/bin/kafka-dump-log.sh --files /var/lib/kafka/data/{T}-0/00000000000000000000.log --print-data-log 2>/dev/null | grep -E 'baseOffset|endTxnMarker' | sed -E 's/ (lastSequence|producerEpoch|partitionLeaderEpoch|deleteHorizonMs|position|CreateTime|size|magic|compresscodec|crc|isvalid|baseSequence|lastOffset): [^ ]*//g' | sed 's/^/  /'"], capture_output=True, text=True).stdout.rstrip())
print("== 6) open transactions known to the cluster")
print(subprocess.run(["docker", "exec", "k1", "/opt/kafka/bin/kafka-transactions.sh", "--bootstrap-server", "k1:9092", "list"], capture_output=True, text=True).stdout.rstrip())
