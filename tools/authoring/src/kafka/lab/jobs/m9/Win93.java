import org.apache.kafka.common.serialization.*;
import org.apache.kafka.streams.*;
import org.apache.kafka.streams.kstream.*;
import java.time.*;
import java.util.*;

public class Win93 {
    static final Instant T0 = Instant.parse("2026-11-06T12:00:00Z");
    static Properties props() {
        Properties p = new Properties();
        p.put(StreamsConfig.APPLICATION_ID_CONFIG, "win-93"); p.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "dummy:9092");
        p.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.StringSerde.class);
        p.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.StringSerde.class);
        p.put(StreamsConfig.STATESTORE_CACHE_MAX_BYTES_CONFIG, 0);
        return p;
    }
    static String w(Windowed<String> k) { return k.key() + "@[" + (k.window().start() - T0.toEpochMilli()) / 1000 + "s," + (k.window().end() - T0.toEpochMilli()) / 1000 + "s)"; }
    static void windowDemo(String title, StreamsBuilder b, String[][] events) {
        System.out.println(title);
        try (TopologyTestDriver d = new TopologyTestDriver(b.build(), props())) {
            TestInputTopic<String, String> in = d.createInputTopic("clicks", new StringSerializer(), new StringSerializer());
            TestOutputTopic<String, String> out = d.createOutputTopic("out", new StringDeserializer(), new StringDeserializer());
            for (String[] e : events) {
                in.pipeInput(e[0], "x", T0.plusSeconds(Long.parseLong(e[1])));
                List<KeyValue<String, String>> r = out.readKeyValuesToList();
                System.out.println("  event " + e[0] + " t=" + e[1] + "s" + (e.length > 2 ? " (" + e[2] + ")" : "") + " -> " + (r.isEmpty() ? "no output" : r.toString()));
            }
        }
    }
    public static void main(String[] a) {
        String[][] ev = {{"Mumbai","1"},{"Mumbai","4"},{"Mumbai","9"},{"Mumbai","12"},{"Mumbai","8","late, within grace"},{"Mumbai","21"},{"Mumbai","7","late, after grace"}};
        // 1 tumbling
        StreamsBuilder b1 = new StreamsBuilder();
        b1.<String,String>stream("clicks").groupByKey().windowedBy(TimeWindows.ofSizeAndGrace(Duration.ofSeconds(10), Duration.ofSeconds(5))).count()
          .toStream().map((k, v) -> KeyValue.pair(w(k), String.valueOf(v))).to("out");
        windowDemo("== 1) tumbling window 10 s, grace 5 s (count per city)", b1, ev);
        // 2 suppress
        StreamsBuilder b2 = new StreamsBuilder();
        b2.<String,String>stream("clicks").groupByKey().windowedBy(TimeWindows.ofSizeAndGrace(Duration.ofSeconds(10), Duration.ofSeconds(5))).count(Materialized.with(Serdes.String(), Serdes.Long()))
          .suppress(Suppressed.untilWindowCloses(Suppressed.BufferConfig.unbounded()))
          .toStream().map((k, v) -> KeyValue.pair(w(k), String.valueOf(v))).to("out");
        windowDemo("== 2) same with suppress(untilWindowCloses): one final result per window", b2, ev);
        // 3 hopping
        StreamsBuilder b3 = new StreamsBuilder();
        b3.<String,String>stream("clicks").groupByKey().windowedBy(TimeWindows.ofSizeWithNoGrace(Duration.ofSeconds(10)).advanceBy(Duration.ofSeconds(5))).count()
          .toStream().map((k, v) -> KeyValue.pair(w(k), String.valueOf(v))).to("out");
        windowDemo("== 3) hopping window 10 s advancing 5 s: one event, two windows", b3, new String[][]{{"Pune","7"}});
        // 4 session
        StreamsBuilder b4 = new StreamsBuilder();
        b4.<String,String>stream("clicks").groupByKey().windowedBy(SessionWindows.ofInactivityGapWithNoGrace(Duration.ofSeconds(5))).count()
          .toStream().map((k, v) -> KeyValue.pair(w(k), v == null ? "deleted (merged)" : String.valueOf(v))).to("out");
        windowDemo("== 4) session window, inactivity gap 5 s", b4, new String[][]{{"Delhi","0"},{"Delhi","3"},{"Delhi","20"},{"Delhi","6","late, no grace"}});
        // 5 stream-table join
        System.out.println("== 5) stream-table join: orders enriched with the latest menu price");
        StreamsBuilder b5 = new StreamsBuilder();
        KTable<String, String> menu = b5.table("menu");
        b5.<String,String>stream("orders").leftJoin(menu, (qty, price) -> price == null ? "qty " + qty + " x ? (not on menu)" : "qty " + qty + " x " + price + " = " + Integer.parseInt(qty) * Integer.parseInt(price)).to("out");
        try (TopologyTestDriver d = new TopologyTestDriver(b5.build(), props())) {
            var m = d.createInputTopic("menu", new StringSerializer(), new StringSerializer());
            var o = d.createInputTopic("orders", new StringSerializer(), new StringSerializer());
            var out = d.createOutputTopic("out", new StringDeserializer(), new StringDeserializer());
            m.pipeInput("idli", "40", T0); m.pipeInput("dosa", "90", T0);
            System.out.println("  menu: idli=40 dosa=90");
            o.pipeInput("idli", "2", T0.plusSeconds(1)); o.pipeInput("pizza", "1", T0.plusSeconds(2));
            System.out.println("  orders idli x2, pizza x1 -> " + out.readKeyValuesToList());
            m.pipeInput("idli", "45", T0.plusSeconds(3)); System.out.println("  menu update idli=45 -> " + (out.isEmpty() ? "no output (table updates do not trigger)" : out.readKeyValuesToList()));
            o.pipeInput("idli", "2", T0.plusSeconds(4)); System.out.println("  order idli x2 -> " + out.readKeyValuesToList());
        }
        // 6 stream-stream join
        System.out.println("== 6) stream-stream join: order + payment within 5 minutes");
        StreamsBuilder b6 = new StreamsBuilder();
        KStream<String,String> ord = b6.stream("orders"); KStream<String,String> pay = b6.stream("payments");
        ord.join(pay, (x, y) -> x + " PAID " + y, JoinWindows.ofTimeDifferenceWithNoGrace(Duration.ofMinutes(5))).to("out");
        try (TopologyTestDriver d = new TopologyTestDriver(b6.build(), props())) {
            var o = d.createInputTopic("orders", new StringSerializer(), new StringSerializer());
            var p = d.createInputTopic("payments", new StringSerializer(), new StringSerializer());
            var out = d.createOutputTopic("out", new StringDeserializer(), new StringDeserializer());
            o.pipeInput("order-1", "idli x2", T0); o.pipeInput("order-2", "dosa x1", T0);
            p.pipeInput("order-1", "Rs 80 UPI", T0.plusSeconds(120));
            System.out.println("  order-1 paid after 2 min -> " + out.readKeyValuesToList());
            p.pipeInput("order-2", "Rs 90 card", T0.plusSeconds(600));
            System.out.println("  order-2 paid after 10 min -> " + (out.isEmpty() ? "no output (outside window)" : out.readKeyValuesToList()));
        }
    }
}
