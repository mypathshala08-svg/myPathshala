// SampleOrders.java: for each item, list the first 3 order ids the reducer sees.
// Run with -D sample.copy=false to see the famous "object reuse" bug.
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.util.GenericOptionsParser;

public class SampleOrders {
  public static class M extends Mapper<LongWritable, Text, Text, Text> {
    private final Text item = new Text(), id = new Text();
    @Override
    protected void map(LongWritable k, Text line, Context ctx) throws IOException, InterruptedException {
      String[] f = line.toString().split(",");
      if (f.length != 3 || f[0].equals("order_id")) return;
      item.set(f[1]); id.set(f[0]);
      ctx.write(item, id);
    }
  }

  public static class R extends Reducer<Text, Text, Text, Text> {
    @Override
    protected void reduce(Text item, Iterable<Text> ids, Context ctx) throws IOException, InterruptedException {
      boolean copy = ctx.getConfiguration().getBoolean("sample.copy", true);
      List<Text> first3 = new ArrayList<>();
      for (Text id : ids) {
        first3.add(copy ? new Text(id) : id);       // without a copy we keep the SAME object 3 times
        if (first3.size() == 3) break;
      }
      ctx.write(item, new Text(first3.toString()));
    }
  }

  public static void main(String[] args) throws Exception {
    Configuration conf = new Configuration();
    String[] rest = new GenericOptionsParser(conf, args).getRemainingArgs();
    Job job = Job.getInstance(conf, "sample orders");
    job.setJarByClass(SampleOrders.class);
    job.setMapperClass(M.class);
    job.setReducerClass(R.class);
    job.setOutputKeyClass(Text.class);
    job.setOutputValueClass(Text.class);
    FileInputFormat.addInputPath(job, new Path(rest[0]));
    FileOutputFormat.setOutputPath(job, new Path(rest[1]));
    System.exit(job.waitForCompletion(true) ? 0 : 1);
  }
}
