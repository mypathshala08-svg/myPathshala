import time
from confluent_kafka.admin import AdminClient, NewTopic
BS = "k1:9092,k2:9092,k3:9092"
def fresh(topic, parts=3, rf=3, config=None):
    a = AdminClient({"bootstrap.servers": BS})
    a.delete_topics([topic]); time.sleep(3)
    a.create_topics([NewTopic(topic, parts, rf, config=config or {})])[topic].result(); time.sleep(2)
