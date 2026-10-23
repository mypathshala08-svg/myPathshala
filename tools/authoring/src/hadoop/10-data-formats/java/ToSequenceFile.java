// ToSequenceFile.java: map-only job. CSV orders -> SequenceFile of (order_id, "student,time,item,amount").
//   -D seq.compress=NONE|RECORD|BLOCK   (codec: -D seq.codec=default|snappy|zstd|gzip)
import java.io.IOException;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.SequenceFile.CompressionType;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.io.compress.*;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.mapreduce.lib.output.SequenceFileOutputFormat;
import org.apache.hadoop.util.GenericOptionsParser;

public class ToSequenceFile {
  public static class M extends Mapper<LongWritable, Text, LongWritable, Text> {
    private final LongWritable id = new LongWritable();
    private final Text rest = new Text();
    @Override
    protected void map(LongWritable k, Text line, Context ctx) throws IOException, InterruptedException {
      String s = line.toString();
      int comma = s.indexOf(',');
      id.set(Long.parseLong(s.substring(0, comma)));
      rest.set(s.substring(comma + 1));
      ctx.write(id, rest);
    }
  }

  static Class<? extends CompressionCodec> codec(String name) {
    switch (name) {
      case "snappy": return SnappyCodec.class;
      case "zstd": return ZStandardCodec.class;
      case "gzip": return GzipCodec.class;
      default: return DefaultCodec.class;           // zlib/deflate
    }
  }

  public static void main(String[] args) throws Exception {
    Configuration conf = new Configuration();
    String[] rest = new GenericOptionsParser(conf, args).getRemainingArgs();
    CompressionType type = CompressionType.valueOf(conf.get("seq.compress", "NONE"));
    Job job = Job.getInstance(conf, "to sequencefile " + type);
    job.setJarByClass(ToSequenceFile.class);
    job.setMapperClass(M.class);
    job.setNumReduceTasks(0);
    job.setOutputKeyClass(LongWritable.class);
    job.setOutputValueClass(Text.class);
    job.setOutputFormatClass(SequenceFileOutputFormat.class);
    if (type != CompressionType.NONE) {
      FileOutputFormat.setCompressOutput(job, true);
      FileOutputFormat.setOutputCompressorClass(job, codec(conf.get("seq.codec", "default")));
      SequenceFileOutputFormat.setOutputCompressionType(job, type);
    }
    FileInputFormat.addInputPath(job, new Path(rest[0]));
    FileOutputFormat.setOutputPath(job, new Path(rest[1]));
    System.exit(job.waitForCompletion(true) ? 0 : 1);
  }
}
