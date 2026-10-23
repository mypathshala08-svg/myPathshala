// ItemRevenue.java: orders per item and revenue per item, as a MapReduce job (new API).
// Input lines: order_id,item,amount      Output: item <TAB> orders <TAB> revenue
import java.io.IOException;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.util.GenericOptionsParser;

public class ItemRevenue {

  public static class OrderMapper extends Mapper<LongWritable, Text, Text, IntWritable> {
    private final Text item = new Text();
    private final IntWritable amount = new IntWritable();

    @Override
    protected void map(LongWritable offset, Text line, Context ctx) throws IOException, InterruptedException {
      String[] f = line.toString().split(",");
      if (f.length != 3 || f[0].equals("order_id")) return;     // skip header / broken lines
      item.set(f[1]);
      amount.set(Integer.parseInt(f[2]));
      ctx.write(item, amount);                                  // ("samosa", 18)
    }
  }

  public static class SumReducer extends Reducer<Text, IntWritable, Text, Text> {
    @Override
    protected void reduce(Text item, Iterable<IntWritable> amounts, Context ctx) throws IOException, InterruptedException {
      long orders = 0, revenue = 0;
      for (IntWritable a : amounts) { orders++; revenue += a.get(); }
      ctx.write(item, new Text(orders + "\t" + revenue));      // samosa  50012  900216
    }
  }

  public static void main(String[] args) throws Exception {
    Configuration conf = new Configuration();
    String[] rest = new GenericOptionsParser(conf, args).getRemainingArgs();   // accepts -D key=value
    Job job = Job.getInstance(conf, "item revenue");
    job.setJarByClass(ItemRevenue.class);
    job.setMapperClass(OrderMapper.class);
    job.setReducerClass(SumReducer.class);
    job.setMapOutputKeyClass(Text.class);
    job.setMapOutputValueClass(IntWritable.class);
    job.setOutputKeyClass(Text.class);
    job.setOutputValueClass(Text.class);
    FileInputFormat.addInputPath(job, new Path(rest[0]));
    FileOutputFormat.setOutputPath(job, new Path(rest[1]));
    System.exit(job.waitForCompletion(true) ? 0 : 1);
  }
}
