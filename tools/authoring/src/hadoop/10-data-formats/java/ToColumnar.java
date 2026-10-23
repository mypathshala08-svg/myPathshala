// ToColumnar.java: map-only job. CSV orders -> Parquet (-D col.format=parquet) or ORC (-D col.format=orc).
//   -D col.codec=UNCOMPRESSED|SNAPPY|ZSTD|GZIP (Parquet)   NONE|SNAPPY|ZSTD|ZLIB (ORC)
import java.io.IOException;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.util.GenericOptionsParser;
import org.apache.orc.OrcConf;
import org.apache.orc.TypeDescription;
import org.apache.orc.mapred.OrcStruct;
import org.apache.orc.mapreduce.OrcOutputFormat;
import org.apache.parquet.example.data.Group;
import org.apache.parquet.example.data.simple.SimpleGroupFactory;
import org.apache.parquet.hadoop.ParquetOutputFormat;
import org.apache.parquet.hadoop.example.ExampleOutputFormat;
import org.apache.parquet.hadoop.example.GroupWriteSupport;
import org.apache.parquet.hadoop.metadata.CompressionCodecName;
import org.apache.parquet.schema.MessageType;
import org.apache.parquet.schema.MessageTypeParser;

public class ToColumnar {
  static final String PARQUET_SCHEMA = "message order { required int64 order_id; required binary student (UTF8); "
      + "required binary time (UTF8); required binary item (UTF8); required int32 amount; }";
  static final String ORC_SCHEMA = "struct<order_id:bigint,student:string,time:string,item:string,amount:int>";

  public static class ParquetMapper extends Mapper<LongWritable, Text, Void, Group> {
    private SimpleGroupFactory factory;
    @Override
    protected void setup(Context ctx) { factory = new SimpleGroupFactory(GroupWriteSupport.getSchema(ctx.getConfiguration())); }
    @Override
    protected void map(LongWritable k, Text line, Context ctx) throws IOException, InterruptedException {
      String[] f = line.toString().split(",");
      Group g = factory.newGroup().append("order_id", Long.parseLong(f[0])).append("student", f[1])
          .append("time", f[2]).append("item", f[3]).append("amount", Integer.parseInt(f[4]));
      ctx.write(null, g);
    }
  }

  public static class OrcMapper extends Mapper<LongWritable, Text, NullWritable, OrcStruct> {
    private final OrcStruct row = (OrcStruct) OrcStruct.createValue(TypeDescription.fromString(ORC_SCHEMA));
    @Override
    protected void map(LongWritable k, Text line, Context ctx) throws IOException, InterruptedException {
      String[] f = line.toString().split(",");
      row.setFieldValue(0, new LongWritable(Long.parseLong(f[0])));
      row.setFieldValue(1, new Text(f[1]));
      row.setFieldValue(2, new Text(f[2]));
      row.setFieldValue(3, new Text(f[3]));
      row.setFieldValue(4, new IntWritable(Integer.parseInt(f[4])));
      ctx.write(NullWritable.get(), row);
    }
  }

  public static void main(String[] args) throws Exception {
    Configuration conf = new Configuration();
    String[] rest = new GenericOptionsParser(conf, args).getRemainingArgs();
    String fmt = conf.get("col.format", "parquet");
    Job job = Job.getInstance(conf, "to " + fmt);
    job.setJarByClass(ToColumnar.class);
    job.setNumReduceTasks(0);
    if (fmt.equals("parquet")) {
      MessageType schema = MessageTypeParser.parseMessageType(PARQUET_SCHEMA);
      GroupWriteSupport.setSchema(schema, job.getConfiguration());
      job.setMapperClass(ParquetMapper.class);
      job.setOutputKeyClass(Void.class);
      job.setOutputValueClass(Group.class);
      job.setOutputFormatClass(ExampleOutputFormat.class);
      ParquetOutputFormat.setCompression(job, CompressionCodecName.valueOf(conf.get("col.codec", "SNAPPY")));
    } else {
      OrcConf.MAPRED_OUTPUT_SCHEMA.setString(job.getConfiguration(), ORC_SCHEMA);
      OrcConf.COMPRESS.setString(job.getConfiguration(), conf.get("col.codec", "ZLIB"));
      job.setMapperClass(OrcMapper.class);
      job.setOutputKeyClass(NullWritable.class);
      job.setOutputValueClass(OrcStruct.class);
      job.setOutputFormatClass(OrcOutputFormat.class);
    }
    FileInputFormat.addInputPath(job, new Path(rest[0]));
    FileOutputFormat.setOutputPath(job, new Path(rest[1]));
    System.exit(job.waitForCompletion(true) ? 0 : 1);
  }
}
