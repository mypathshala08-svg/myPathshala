// CleanOrders.java: a map-only job. Keeps good orders, counts bad ones with custom counters,
// and logs the Mapper lifecycle (setup -> map ... -> cleanup) to the task log.
import java.io.IOException;
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

public class CleanOrders {
  enum Quality { GOOD, HEADER, WRONG_FIELDS, BAD_AMOUNT }

  public static class CleanMapper extends Mapper<LongWritable, Text, NullWritable, Text> {
    private final Text out = new Text();
    private long calls = 0;

    @Override
    protected void setup(Context ctx) {
      System.err.println("setup()   once, before the first record. split = " + ctx.getInputSplit());
    }

    @Override
    protected void map(LongWritable offset, Text line, Context ctx) throws IOException, InterruptedException {
      calls++;
      String[] f = line.toString().split(",");
      if (f[0].equals("order_id")) { ctx.getCounter(Quality.HEADER).increment(1); return; }
      if (f.length != 3) { ctx.getCounter(Quality.WRONG_FIELDS).increment(1); return; }
      int amount;
      try { amount = Integer.parseInt(f[2].trim()); }
      catch (NumberFormatException e) { ctx.getCounter(Quality.BAD_AMOUNT).increment(1); return; }
      if (amount <= 0) { ctx.getCounter(Quality.BAD_AMOUNT).increment(1); return; }
      ctx.getCounter(Quality.GOOD).increment(1);
      out.set(f[0] + "," + f[1].trim().toLowerCase() + "," + amount);
      ctx.write(NullWritable.get(), out);
    }

    @Override
    protected void cleanup(Context ctx) {
      System.err.println("cleanup() once, after the last record. map() was called " + calls + " times");
    }
  }

  public static void main(String[] args) throws Exception {
    Configuration conf = new Configuration();
    String[] rest = new GenericOptionsParser(conf, args).getRemainingArgs();
    Job job = Job.getInstance(conf, "clean orders");
    job.setJarByClass(CleanOrders.class);
    job.setMapperClass(CleanMapper.class);
    job.setNumReduceTasks(0);
    job.setOutputKeyClass(NullWritable.class);
    job.setOutputValueClass(Text.class);
    FileInputFormat.addInputPath(job, new Path(rest[0]));
    FileOutputFormat.setOutputPath(job, new Path(rest[1]));
    System.exit(job.waitForCompletion(true) ? 0 : 1);
  }
}
