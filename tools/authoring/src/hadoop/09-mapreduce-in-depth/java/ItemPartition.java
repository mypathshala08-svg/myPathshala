// ItemPartition.java: orders and revenue per item with 4 reducers.
// -D part.mode=hash      default HashPartitioner
// -D part.mode=counter   CounterPartitioner: every item of one canteen counter (A–D) goes to the same reducer
// -D part.mode=bad       BadPartitioner (BadPartitioner.java): returns an invalid partition number
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Partitioner;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.util.GenericOptionsParser;

public class ItemPartition {
  public static class M extends Mapper<LongWritable, Text, Text, IntWritable> {
    private final Text item = new Text();
    private final IntWritable amount = new IntWritable();
    @Override
    protected void map(LongWritable k, Text line, Context ctx) throws IOException, InterruptedException {
      String[] f = line.toString().split(",");          // order_id,student_id,time,item,amount
      item.set(f[3]); amount.set(Integer.parseInt(f[4]));
      ctx.write(item, amount);
    }
  }

  // Counter A: chai, coffee   B: samosa, vada pav   C: poha, idli   D: dosa, thali
  public static class CounterPartitioner extends Partitioner<Text, IntWritable> {
    private static final Map<String, Integer> COUNTER = new HashMap<>();
    static {
      COUNTER.put("chai", 0); COUNTER.put("coffee", 0); COUNTER.put("samosa", 1); COUNTER.put("vada pav", 1);
      COUNTER.put("poha", 2); COUNTER.put("idli", 2); COUNTER.put("dosa", 3); COUNTER.put("thali", 3);
    }
    @Override
    public int getPartition(Text item, IntWritable amount, int numReduceTasks) {
      Integer c = COUNTER.get(item.toString());
      if (c == null) return 0;                           // unknown items go to the first reducer
      return c % numReduceTasks;                         // must always be in 0 .. numReduceTasks-1
    }
  }

  public static class R extends Reducer<Text, IntWritable, Text, Text> {
    @Override
    protected void reduce(Text item, Iterable<IntWritable> amounts, Context ctx) throws IOException, InterruptedException {
      long n = 0, sum = 0;
      for (IntWritable a : amounts) { n++; sum += a.get(); }
      ctx.write(item, new Text(n + "\t" + sum));
    }
  }

  public static void main(String[] args) throws Exception {
    Configuration conf = new Configuration();
    String[] rest = new GenericOptionsParser(conf, args).getRemainingArgs();
    String mode = conf.get("part.mode", "hash");
    Job job = Job.getInstance(conf, "item partition " + mode);
    job.setJarByClass(ItemPartition.class);
    job.setMapperClass(M.class);
    job.setReducerClass(R.class);
    if (mode.equals("counter")) job.setPartitionerClass(CounterPartitioner.class);
    if (mode.equals("bad")) job.setPartitionerClass(BadPartitioner.class);
    job.setNumReduceTasks(conf.getInt("part.reducers", 4));           // -D part.reducers=N to change
    job.setMapOutputKeyClass(Text.class);
    job.setMapOutputValueClass(IntWritable.class);
    job.setOutputKeyClass(Text.class);
    job.setOutputValueClass(Text.class);
    FileInputFormat.addInputPath(job, new Path(rest[0]));
    FileOutputFormat.setOutputPath(job, new Path(rest[1]));
    System.exit(job.waitForCompletion(true) ? 0 : 1);
  }
}
