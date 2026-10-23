// ItemCountAny.java: orders per item, reading any of our formats.  -D in.format=text|seq|avro|parquet|orc
// For parquet and orc only the "item" column is requested (column projection); -D proj=false reads all columns.
import java.io.IOException;
import org.apache.avro.Schema;
import org.apache.avro.generic.GenericRecord;
import org.apache.avro.mapred.AvroKey;
import org.apache.avro.mapreduce.AvroJob;
import org.apache.avro.mapreduce.AvroKeyInputFormat;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.input.SequenceFileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.mapreduce.lib.reduce.LongSumReducer;
import org.apache.hadoop.util.GenericOptionsParser;
import org.apache.orc.OrcConf;
import org.apache.orc.mapred.OrcStruct;
import org.apache.orc.mapreduce.OrcInputFormat;
import org.apache.parquet.example.data.Group;
import org.apache.parquet.hadoop.example.ExampleInputFormat;

public class ItemCountAny {
  static final LongWritable ONE = new LongWritable(1);

  public static class TextM extends Mapper<LongWritable, Text, Text, LongWritable> {
    private final Text item = new Text();
    @Override protected void map(LongWritable k, Text v, Context c) throws IOException, InterruptedException {
      item.set(v.toString().split(",")[3]); c.write(item, ONE);
    }
  }
  public static class SeqM extends Mapper<LongWritable, Text, Text, LongWritable> {   // value = student,time,item,amount
    private final Text item = new Text();
    @Override protected void map(LongWritable k, Text v, Context c) throws IOException, InterruptedException {
      item.set(v.toString().split(",")[2]); c.write(item, ONE);
    }
  }
  public static class AvroM extends Mapper<AvroKey<GenericRecord>, NullWritable, Text, LongWritable> {
    private final Text item = new Text();
    @Override protected void map(AvroKey<GenericRecord> k, NullWritable v, Context c) throws IOException, InterruptedException {
      item.set(k.datum().get("item").toString()); c.write(item, ONE);
    }
  }
  public static class ParquetM extends Mapper<Void, Group, Text, LongWritable> {
    private final Text item = new Text();
    @Override protected void map(Void k, Group g, Context c) throws IOException, InterruptedException {
      item.set(g.getString("item", 0)); c.write(item, ONE);
    }
  }
  public static class OrcM extends Mapper<NullWritable, OrcStruct, Text, LongWritable> {
    @Override protected void map(NullWritable k, OrcStruct row, Context c) throws IOException, InterruptedException {
      c.write((Text) row.getFieldValue("item"), ONE);
    }
  }

  public static void main(String[] args) throws Exception {
    Configuration conf = new Configuration();
    String[] rest = new GenericOptionsParser(conf, args).getRemainingArgs();
    String fmt = conf.get("in.format", "text");
    Job job = Job.getInstance(conf, "item count from " + fmt);
    job.setJarByClass(ItemCountAny.class);
    switch (fmt) {
      case "seq": job.setInputFormatClass(SequenceFileInputFormat.class); job.setMapperClass(SeqM.class); break;
      case "avro":
        job.setInputFormatClass(AvroKeyInputFormat.class);
        AvroJob.setInputKeySchema(job, new Schema.Parser().parse(ToAvro.SCHEMA));
        job.setMapperClass(AvroM.class); break;
      case "parquet":
        job.setInputFormatClass(ExampleInputFormat.class);
        if (conf.getBoolean("proj", true))
          job.getConfiguration().set("parquet.read.schema", "message order { required binary item (UTF8); }");   // projection
        job.setMapperClass(ParquetM.class); break;
      case "orc":
        job.setInputFormatClass(OrcInputFormat.class);
        if (conf.getBoolean("proj", true))
          OrcConf.INCLUDE_COLUMNS.setString(job.getConfiguration(), "3");                                       // only column 3: item
        job.setMapperClass(OrcM.class); break;
      default: job.setMapperClass(TextM.class);
    }
    job.setCombinerClass(LongSumReducer.class);
    job.setReducerClass(LongSumReducer.class);
    job.setOutputKeyClass(Text.class);
    job.setOutputValueClass(LongWritable.class);
    FileInputFormat.addInputPath(job, new Path(rest[0]));
    FileOutputFormat.setOutputPath(job, new Path(rest[1]));
    System.exit(job.waitForCompletion(true) ? 0 : 1);
  }
}
