// HeapHog.java: a deliberately memory-hungry map-only job. Each map task keeps EVERY line it reads
// in a list (a common real-world bug: collecting instead of streaming), then writes how many it kept.
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
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.util.GenericOptionsParser;

public class HeapHog {
  public static class M extends Mapper<LongWritable, Text, NullWritable, Text> {
    private final List<String> kept = new ArrayList<>();
    @Override
    protected void map(LongWritable k, Text line, Context ctx) { kept.add(line.toString()); }
    @Override
    protected void cleanup(Context ctx) throws IOException, InterruptedException {
      Runtime r = Runtime.getRuntime();
      String msg = String.format("kept %,d lines; heap used %d MB of max %d MB", kept.size(),
          (r.totalMemory() - r.freeMemory()) >> 20, r.maxMemory() >> 20);
      System.err.println(msg);
      ctx.write(NullWritable.get(), new Text(msg));
    }
  }

  public static void main(String[] args) throws Exception {
    Configuration conf = new Configuration();
    String[] rest = new GenericOptionsParser(conf, args).getRemainingArgs();
    Job job = Job.getInstance(conf, "heap hog");
    job.setJarByClass(HeapHog.class);
    job.setMapperClass(M.class);
    job.setNumReduceTasks(0);
    job.setOutputKeyClass(NullWritable.class);
    job.setOutputValueClass(Text.class);
    FileInputFormat.addInputPath(job, new Path(rest[0]));
    FileOutputFormat.setOutputPath(job, new Path(rest[1]));
    System.exit(job.waitForCompletion(true) ? 0 : 1);
  }
}
