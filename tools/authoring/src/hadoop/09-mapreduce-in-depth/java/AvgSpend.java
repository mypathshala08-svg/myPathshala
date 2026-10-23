// AvgSpend.java: average amount per order for each student.
// -D avg.combiner=wrong   uses the averaging reducer as a combiner (gives WRONG answers)
// -D avg.combiner=right   map emits (sum,count) pairs and the combiner adds them (correct)
// -D avg.combiner=none    no combiner (correct, more data shuffled)
import java.io.IOException;
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

public class AvgSpend {
  // value travels as text "sum,count" so the same reducer can read map output and combiner output
  public static class M extends Mapper<LongWritable, Text, Text, Text> {
    private final Text student = new Text(), val = new Text();
    @Override
    protected void map(LongWritable k, Text line, Context ctx) throws IOException, InterruptedException {
      String[] f = line.toString().split(",");          // order_id,student_id,time,item,amount
      student.set(f[1]);
      val.set(f[4] + ",1");
      ctx.write(student, val);
    }
  }

  // WRONG as a combiner: it averages its input and claims the result is 1 order, so averages get averaged
  public static class AvgReducer extends Reducer<Text, Text, Text, Text> {
    @Override
    protected void reduce(Text s, Iterable<Text> vals, Context ctx) throws IOException, InterruptedException {
      double sum = 0; long n = 0;
      for (Text v : vals) { String[] p = v.toString().split(","); sum += Double.parseDouble(p[0]); n += 1; }   // ignores the counts
      ctx.write(s, new Text((sum / n) + ",1"));                  // a partial AVERAGE, pretending to be 1 order
    }
  }

  // RIGHT as a combiner: adds sums and counts, never divides
  public static class SumCountCombiner extends Reducer<Text, Text, Text, Text> {
    @Override
    protected void reduce(Text s, Iterable<Text> vals, Context ctx) throws IOException, InterruptedException {
      double sum = 0; long n = 0;
      for (Text v : vals) { String[] p = v.toString().split(","); sum += Double.parseDouble(p[0]); n += Long.parseLong(p[1]); }
      ctx.write(s, new Text(sum + "," + n));
    }
  }

  // Final reducer for the correct versions: divide once at the end
  public static class FinalAvg extends Reducer<Text, Text, Text, Text> {
    @Override
    protected void reduce(Text s, Iterable<Text> vals, Context ctx) throws IOException, InterruptedException {
      double sum = 0; long n = 0;
      for (Text v : vals) { String[] p = v.toString().split(","); sum += Double.parseDouble(p[0]); n += Long.parseLong(p[1]); }
      ctx.write(s, new Text(String.format("%.2f (%d orders)", sum / n, n)));
    }
  }

  public static void main(String[] args) throws Exception {
    Configuration conf = new Configuration();
    String[] rest = new GenericOptionsParser(conf, args).getRemainingArgs();
    String mode = conf.get("avg.combiner", "none");
    Job job = Job.getInstance(conf, "avg spend combiner=" + mode);
    job.setJarByClass(AvgSpend.class);
    job.setMapperClass(M.class);
    if (mode.equals("wrong")) job.setCombinerClass(AvgReducer.class);
    if (mode.equals("right")) job.setCombinerClass(SumCountCombiner.class);
    job.setReducerClass(FinalAvg.class);
    job.setOutputKeyClass(Text.class);
    job.setOutputValueClass(Text.class);
    FileInputFormat.addInputPath(job, new Path(rest[0]));
    FileOutputFormat.setOutputPath(job, new Path(rest[1]));
    System.exit(job.waitForCompletion(true) ? 0 : 1);
  }
}
