import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.streams.*;
import org.apache.kafka.streams.kstream.*;
import java.util.Properties;

public class Kitchen91 {
    public static void main(String[] a) throws Exception {
        StreamsBuilder b = new StreamsBuilder();
        KStream<String, String> orders = b.stream("orders-91");          // key = city, value = item,qty,price
        KStream<String, String> valid = orders
            .peek((k, v) -> System.out.println("  in   " + k + " -> " + v))
            .filter((k, v) -> Integer.parseInt(v.split(",")[1]) > 0)     // drop qty 0
            .mapValues(v -> v.toUpperCase());
        valid.split()
            .branch((k, v) -> v.startsWith("THALI"), Branched.withConsumer(s -> s.to("big-orders-91")))
            .defaultBranch(Branched.withConsumer(s -> s.to("small-orders-91")));
        Topology t = b.build();
        System.out.println("== topology");
        System.out.println(t.describe());
        Properties p = new Properties();
        p.put(StreamsConfig.APPLICATION_ID_CONFIG, "kitchen-91");
        p.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "k1:9092,k2:9092,k3:9092");
        p.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.StringSerde.class);
        p.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.StringSerde.class);
        p.put(StreamsConfig.NUM_STREAM_THREADS_CONFIG, a.length > 0 ? a[0] : "1");
        p.put("consumer.auto.offset.reset", "earliest");
        KafkaStreams ks = new KafkaStreams(t, p);
        ks.setStateListener((n, o) -> System.out.println("  state " + o + " -> " + n));
        ks.start();
        Thread.sleep(Long.parseLong(a.length > 1 ? a[1] : "20000"));
        System.out.println("== tasks");
        for (var th : ks.metadataForLocalThreads())
            th.activeTasks().forEach(tk -> System.out.println("  " + th.threadName().replaceAll(".*-(StreamThread-\\d+)", "$1") + " task " + tk.taskId() + " partitions " + tk.topicPartitions()));
        ks.close();
    }
}
