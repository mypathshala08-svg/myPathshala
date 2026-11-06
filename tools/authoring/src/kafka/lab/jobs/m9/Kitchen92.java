import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.common.TopicPartition;
import org.apache.kafka.streams.*;
import org.apache.kafka.streams.kstream.*;
import org.apache.kafka.streams.processor.StateRestoreListener;
import org.apache.kafka.streams.state.*;
import java.util.Properties;

public class Kitchen92 {
    public static void main(String[] a) throws Exception {
        StreamsBuilder b = new StreamsBuilder();
        KStream<String, String> orders = b.stream("orders-92");            // key = city, value = item
        KTable<String, Long> perItem = orders
            .groupBy((city, item) -> item)                                   // re-key by item -> repartition
            .count(Materialized.<String, Long, KeyValueStore<org.apache.kafka.common.utils.Bytes, byte[]>>as("item-counts"));
        perItem.toStream().to("item-counts-92", Produced.with(Serdes.String(), Serdes.Long()));
        Properties p = new Properties();
        p.put(StreamsConfig.APPLICATION_ID_CONFIG, "kitchen-92");
        p.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "k1:9092,k2:9092,k3:9092");
        p.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.StringSerde.class);
        p.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.StringSerde.class);
        p.put(StreamsConfig.STATE_DIR_CONFIG, "/tmp/kstate");
        p.put(StreamsConfig.STATESTORE_CACHE_MAX_BYTES_CONFIG, 0);   // emit every update (no cache) for teaching
        p.put(StreamsConfig.REPLICATION_FACTOR_CONFIG, 3);
        p.put("consumer.auto.offset.reset", "earliest");
        KafkaStreams ks = new KafkaStreams(b.build(), p);
        ks.setGlobalStateRestoreListener(new StateRestoreListener() {
            public void onRestoreStart(TopicPartition tp, String s, long from, long to) { System.out.println("  restore " + s + " from " + tp + " offsets " + from + ".." + to); }
            public void onBatchRestored(TopicPartition tp, String s, long end, long n) {}
            public void onRestoreEnd(TopicPartition tp, String s, long n) { System.out.println("  restored " + n + " records into " + s); }
        });
        ks.start();
        Thread.sleep(Long.parseLong(a[0]));
        for (int i = 0; i < 120 && ks.state() != KafkaStreams.State.RUNNING; i++) Thread.sleep(500);
        System.out.println("  app state " + ks.state());
        ReadOnlyKeyValueStore<String, Long> st = ks.store(StoreQueryParameters.fromNameAndType("item-counts", QueryableStoreTypes.keyValueStore()));
        StringBuilder sb = new StringBuilder("  store item-counts:");
        try (var it = st.all()) { while (it.hasNext()) { var kv = it.next(); sb.append(" ").append(kv.key).append("=").append(kv.value); } }
        System.out.println(sb);
        ks.close(java.time.Duration.ofSeconds(10));
        System.exit(0);
    }
}
