// ToAvro.java: map-only job. CSV orders -> Avro data files with an explicit schema.
//   -D avro.codec=null|deflate|snappy|zstandard
import java.io.IOException;
import org.apache.avro.Schema;
import org.apache.avro.generic.GenericData;
import org.apache.avro.generic.GenericRecord;
import org.apache.avro.mapred.AvroKey;
import org.apache.avro.mapreduce.AvroJob;
import org.apache.avro.mapreduce.AvroKeyOutputFormat;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.util.GenericOptionsParser;

public class ToAvro {
  static final String SCHEMA = "{\"type\":\"record\",\"name\":\"Order\",\"namespace\":\"in.myphatshala\",\"fields\":["
      + "{\"name\":\"order_id\",\"type\":\"long\"},"
      + "{\"name\":\"student\",\"type\":\"string\"},"
      + "{\"name\":\"time\",\"type\":\"string\"},"
      + "{\"name\":\"item\",\"type\":\"string\"},"
      + "{\"name\":\"amount\",\"type\":\"int\"}]}";

  public static class M extends Mapper<LongWritable, Text, AvroKey<GenericRecord>, NullWritable> {
    private Schema schema;
    private GenericRecord rec;
    private final AvroKey<GenericRecord> out = new AvroKey<>();
    @Override
    protected void setup(Context ctx) { schema = new Schema.Parser().parse(SCHEMA); rec = new GenericData.Record(schema); }
    @Override
    protected void map(LongWritable k, Text line, Context ctx) throws IOException, InterruptedException {
      String[] f = line.toString().split(",");
      rec.put("order_id", Long.parseLong(f[0]));
      rec.put("student", f[1]);
      rec.put("time", f[2]);
      rec.put("item", f[3]);
      rec.put("amount", Integer.parseInt(f[4]));
      out.datum(rec);
      ctx.write(out, NullWritable.get());
    }
  }

  public static void main(String[] args) throws Exception {
    Configuration conf = new Configuration();
    String[] rest = new GenericOptionsParser(conf, args).getRemainingArgs();
    Job job = Job.getInstance(conf, "to avro " + conf.get("avro.codec", "deflate"));
    job.setJarByClass(ToAvro.class);
    job.setMapperClass(M.class);
    job.setNumReduceTasks(0);
    AvroJob.setOutputKeySchema(job, new Schema.Parser().parse(SCHEMA));
    job.setOutputFormatClass(AvroKeyOutputFormat.class);
    String codec = conf.get("avro.codec", "deflate");
    if (!codec.equals("null")) { FileOutputFormat.setCompressOutput(job, true); job.getConfiguration().set("avro.output.codec", codec); }
    FileInputFormat.addInputPath(job, new Path(rest[0]));
    FileOutputFormat.setOutputPath(job, new Path(rest[1]));
    System.exit(job.waitForCompletion(true) ? 0 : 1);
  }
}
