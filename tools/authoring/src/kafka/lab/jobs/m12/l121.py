# Capstone design: from requirements to Kafka decisions
import math
req = {"orders_peak_per_s": 2000, "order_kb": 0.5, "consumers_max": 6, "latency_slo_s": 60,
       "keep_days": 7, "must_not_lose": True, "order_per_city": True, "bad_orders_pct": 5}
print("== 1) requirements")
for k, v in req.items(): print(f"  {k:20s} {v}")
mb = req["orders_peak_per_s"] * req["order_kb"] / 1024
parts = max(math.ceil(mb / 5), req["consumers_max"])
print("== 2) decisions derived")
print(f"  cap-orders: {parts} partitions (peak {mb:.2f} MB/s, {req['consumers_max']} consumers), key = city (order per city)")
print(f"  durability: RF 3, min.insync.replicas 2, producer acks=all + idempotence (must_not_lose)")
print(f"  retention: {req['keep_days']} days; cap-menu compacted (latest price per item)")
print(f"  processing: read_committed + transactions (exactly-once into enriched + DLQ)")
print(f"  errors: ~{req['bad_orders_pct']}% expected → cap-orders-dlq with x-error headers")
print(f"  contract: Avro + Schema Registry (BACKWARD); sink: Kafka Connect")
print(f"  SLO: alert if lag > {req['latency_slo_s']} s of processing")
print("== 3) topic plan")
for t, p, c in [("cap-orders", parts, "delete, 7d, min ISR 2"), ("cap-menu", 3, "compact"), ("cap-orders-enriched", 3, "delete, min ISR 2"), ("cap-orders-dlq", 3, "delete, 30d")]:
    print(f"  {t:22s} partitions {p:2d}  RF 3  {c}")
