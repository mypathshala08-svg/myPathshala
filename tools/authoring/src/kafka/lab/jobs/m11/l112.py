import time, subprocess, pika
from confluent_kafka import Producer, Consumer, TopicPartition
from confluent_kafka.admin import AdminClient, NewTopic
orders = [f"order-{i}" for i in range(1, 6)]
print("== 1) RabbitMQ 4: a quorum queue, two consumers on it, then a late consumer")
for i in range(20):
    try: conn = pika.BlockingConnection(pika.ConnectionParameters('localhost')); break
    except Exception: time.sleep(2)
ch = conn.channel(); ch.queue_delete(queue='orders-112'); ch.queue_declare(queue='orders-112', durable=True, arguments={'x-queue-type': 'quorum'})
ch.confirm_delivery()
for o in orders: ch.basic_publish(exchange='', routing_key='orders-112', body=o)
print("  published 5; queue depth:", ch.queue_declare(queue='orders-112', passive=True).method.message_count)
got = {'A': [], 'B': []}
for n in range(5):
    who = 'A' if n % 2 == 0 else 'B'
    m, props, body = ch.basic_get('orders-112')
    got[who].append(body.decode()); ch.basic_ack(m.delivery_tag)
print("  consumer A got", got['A'], " consumer B got", got['B'], " (competing consumers)")
print("  queue depth after acks:", ch.queue_declare(queue='orders-112', passive=True).method.message_count)
m = ch.basic_get('orders-112')[0]
print("  late consumer C (billing) gets:", "nothing, messages are gone after ack" if m is None else m)
v = subprocess.run(['docker','exec','rmq','rabbitmqctl','version'],capture_output=True,text=True).stdout.strip()
print("  RabbitMQ version:", v)
conn.close()
print("== 2) Kafka 4.4: same 5 orders in a topic, two groups, then replay")
BS = 'k2:9092'
a = AdminClient({'bootstrap.servers': BS}); a.delete_topics(['orders-112']); time.sleep(3)
a.create_topics([NewTopic('orders-112', 1, 3)])['orders-112'].result()
p = Producer({'bootstrap.servers': BS})
for o in orders: p.produce('orders-112', o.encode())
p.flush()
def read(group, reset=None):
    c = Consumer({'bootstrap.servers': BS, 'group.id': group, 'auto.offset.reset': 'earliest'})
    c.subscribe(['orders-112']); out = []; t0 = time.time()
    while len(out) < 5 and time.time() - t0 < 15:
        m = c.poll(0.5)
        if m and not m.error(): out.append(m.value().decode())
    c.close(); return out
k = read('kitchen-112-%d' % time.time()); b = read('billing-112-%d' % time.time())
print("  group kitchen got", k)
print("  group billing got", b, " (each group gets everything)")
end = Consumer({'bootstrap.servers': BS, 'group.id': 'x'}).get_watermark_offsets(TopicPartition('orders-112', 0))
print("  records still in the topic after both read:", end[1] - end[0])
print("  replay: a new group (or an offset reset) reads them again:", read('audit-112-%d' % time.time())[:3], "...")
