// JoinReduceSide.java: reduce-side join of orders with the menu.
// Both inputs are mapped to (item, tagged record); the reducer meets them per item and writes
// every order with its category added.
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.MultipleInputs;
import org.apache.hadoop.mapreduce.lib.input.TextInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.util.GenericOptionsParser;

public class JoinReduceSide {
  enum Join { ORDERS_JOINED, ORDERS_WITHOUT_MENU, MENU_FIRST, MENU_NOT_FIRST }

  // orders: order_id,student_id,time,item,amount   ->  (item, "O|whole line")
  public static class OrderMapper extends Mapper<LongWritable, Text, Text, Text> {
    private final Text item = new Text(), val = new Text();
    @Override
    protected void map(LongWritable k, Text line, Context ctx) throws IOException, InterruptedException {
      item.set(line.toString().split(",")[3]);
      val.set("O|" + line);
      ctx.write(item, val);
    }
  }

  // menu: item,category,price,counter   ->  (item, "M|category")
  public static class MenuMapper extends Mapper<LongWritable, Text, Text, Text> {
    private final Text item = new Text(), val = new Text();
    @Override
    protected void map(LongWritable k, Text line, Context ctx) throws IOException, InterruptedException {
      String[] f = line.toString().split(",");
      item.set(f[0]); val.set("M|" + f[1]);
      ctx.write(item, val);
    }
  }

  // For one item: one menu record and thousands of order records, in NO particular order
  public static class JoinReducer extends Reducer<Text, Text, Text, NullWritable> {
    private final Text out = new Text();
    @Override
    protected void reduce(Text item, Iterable<Text> vals, Context ctx) throws IOException, InterruptedException {
      String category = null;
      List<String> orders = new ArrayList<>();         // must buffer: the menu record may arrive last
      boolean first = true;
      for (Text v : vals) {
        String s = v.toString();
        if (s.startsWith("M|")) {
          category = s.substring(2);
          ctx.getCounter(first ? Join.MENU_FIRST : Join.MENU_NOT_FIRST).increment(1);
        } else orders.add(s.substring(2));
        first = false;
      }
      if (category == null) { ctx.getCounter(Join.ORDERS_WITHOUT_MENU).increment(orders.size()); return; }
      for (String o : orders) { out.set(o + "," + category); ctx.write(out, NullWritable.get()); }
      ctx.getCounter(Join.ORDERS_JOINED).increment(orders.size());
    }
  }

  public static void main(String[] args) throws Exception {
    Configuration conf = new Configuration();
    String[] rest = new GenericOptionsParser(conf, args).getRemainingArgs();   // orders menu out
    Job job = Job.getInstance(conf, "reduce-side join");
    job.setJarByClass(JoinReduceSide.class);
    MultipleInputs.addInputPath(job, new Path(rest[0]), TextInputFormat.class, OrderMapper.class);
    MultipleInputs.addInputPath(job, new Path(rest[1]), TextInputFormat.class, MenuMapper.class);
    job.setReducerClass(JoinReducer.class);
    job.setMapOutputKeyClass(Text.class);
    job.setMapOutputValueClass(Text.class);
    job.setOutputKeyClass(Text.class);
    job.setOutputValueClass(NullWritable.class);
    FileOutputFormat.setOutputPath(job, new Path(rest[2]));
    System.exit(job.waitForCompletion(true) ? 0 : 1);
  }
}
