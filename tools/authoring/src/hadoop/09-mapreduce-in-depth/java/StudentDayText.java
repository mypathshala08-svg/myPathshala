// StudentDayText.java: the same job as StudentDay, but key and value travel as Text strings.
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

public class StudentDayText {
  public static class M extends Mapper<LongWritable, Text, Text, Text> {
    private final Text key = new Text(), val = new Text();
    @Override
    protected void map(LongWritable k, Text line, Context ctx) throws IOException, InterruptedException {
      String[] f = line.toString().split(",");
      key.set(f[1] + "\t" + f[2].substring(0, 10));
      val.set("1," + f[4] + "," + f[4]);
      ctx.write(key, val);
    }
  }
  public static class R extends Reducer<Text, Text, Text, Text> {
    @Override
    protected void reduce(Text k, Iterable<Text> vals, Context ctx) throws IOException, InterruptedException {
      int orders = 0, max = 0; long total = 0;
      for (Text v : vals) {
        String[] p = v.toString().split(",");
        orders += Integer.parseInt(p[0]); total += Long.parseLong(p[1]); max = Math.max(max, Integer.parseInt(p[2]));
      }
      ctx.write(k, new Text(orders + "," + total + "," + max));
    }
  }
  public static void main(String[] args) throws Exception {
    Configuration conf = new Configuration();
    String[] rest = new GenericOptionsParser(conf, args).getRemainingArgs();
    Job job = Job.getInstance(conf, "student day text");
    job.setJarByClass(StudentDayText.class);
    job.setMapperClass(M.class);
    job.setCombinerClass(R.class);
    job.setReducerClass(R.class);
    job.setOutputKeyClass(Text.class);
    job.setOutputValueClass(Text.class);
    FileInputFormat.addInputPath(job, new Path(rest[0]));
    FileOutputFormat.setOutputPath(job, new Path(rest[1]));
    System.exit(job.waitForCompletion(true) ? 0 : 1);
  }
}
