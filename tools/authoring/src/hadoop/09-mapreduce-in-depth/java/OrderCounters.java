// OrderCounters.java: a map-only job that only counts. Enum counters, dynamic counters,
// and reading every counter back in the driver after the job.
// -D counters.perStudent=true adds one dynamic counter per student (to hit the counter limit)
import java.io.IOException;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Counter;
import org.apache.hadoop.mapreduce.CounterGroup;
import org.apache.hadoop.mapreduce.Counters;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.TaskCounter;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.NullOutputFormat;
import org.apache.hadoop.util.GenericOptionsParser;

public class OrderCounters {
  enum Category { DRINK, SNACK, BREAKFAST, MEAL, UNKNOWN }

  public static class M extends Mapper<LongWritable, Text, NullWritable, NullWritable> {
    private boolean perStudent;
    @Override
    protected void setup(Context ctx) { perStudent = ctx.getConfiguration().getBoolean("counters.perStudent", false); }

    @Override
    protected void map(LongWritable k, Text line, Context ctx) {
      String[] f = line.toString().split(",");          // order_id,student_id,time,item,amount
      String item = f[3];
      Category c;
      switch (item) {
        case "chai": case "coffee": c = Category.DRINK; break;
        case "samosa": case "vada pav": c = Category.SNACK; break;
        case "poha": case "idli": c = Category.BREAKFAST; break;
        case "dosa": case "thali": c = Category.MEAL; break;
        default: c = Category.UNKNOWN;
      }
      ctx.getCounter(c).increment(1);                             // enum counter
      ctx.getCounter("Orders by hour", f[2].substring(11, 13)).increment(1);   // dynamic counter: group, name
      ctx.getCounter("Revenue (Rs)", c.name()).increment(Long.parseLong(f[4]));
      if (perStudent) ctx.getCounter("Orders by student", f[1]).increment(1);
    }
  }

  public static void main(String[] args) throws Exception {
    Configuration conf = new Configuration();
    String[] rest = new GenericOptionsParser(conf, args).getRemainingArgs();
    Job job = Job.getInstance(conf, "order counters");
    job.setJarByClass(OrderCounters.class);
    job.setMapperClass(M.class);
    job.setNumReduceTasks(0);
    job.setOutputFormatClass(NullOutputFormat.class);            // no output files at all
    FileInputFormat.addInputPath(job, new Path(rest[0]));
    boolean ok = job.waitForCompletion(false);                   // false: don't print progress and counters

    // The driver reads the final counters and decides what to do with them
    Counters cs = job.getCounters();
    long in = cs.findCounter(TaskCounter.MAP_INPUT_RECORDS).getValue();
    System.out.println("job " + (ok ? "SUCCEEDED" : "FAILED") + ", map input records = " + in);
    for (String group : new String[] {OrderCounters.Category.class.getName(), "Orders by hour", "Revenue (Rs)"}) {
      CounterGroup g = cs.getGroup(group);
      System.out.println("[" + g.getDisplayName() + "]");
      for (Counter c : g) System.out.printf("  %-10s %,d%n", c.getDisplayName(), c.getValue());
    }
    if (cs.findCounter(Category.UNKNOWN).getValue() > 0) { System.out.println("unknown items found!"); System.exit(2); }
    System.exit(ok ? 0 : 1);
  }
}
