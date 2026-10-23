// JoinMapSide.java: map-side join, a map-only job. The small menu is shipped to every map task
// with the distributed cache and loaded into a HashMap in setup(); orders are joined as they are read.
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.net.URI;
import java.util.HashMap;
import java.util.Map;
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

public class JoinMapSide {
  enum Join { ORDERS_JOINED, ORDERS_WITHOUT_MENU }

  public static class JoinMapper extends Mapper<LongWritable, Text, Text, NullWritable> {
    private final Map<String, String> category = new HashMap<>();
    private final Text out = new Text();

    @Override
    protected void setup(Context ctx) throws IOException {
      URI[] files = ctx.getCacheFiles();
      System.err.println("cache files: " + java.util.Arrays.toString(files));
      // "#menu" in the URI makes YARN create a symlink called "menu" in the task's working directory
      try (BufferedReader r = new BufferedReader(new FileReader("menu"))) {
        String line;
        while ((line = r.readLine()) != null) {
          String[] f = line.split(",");
          category.put(f[0], f[1]);
        }
      }
      System.err.println("menu loaded in setup(): " + category.size() + " items, working dir = " + new java.io.File(".").getAbsolutePath());
    }

    @Override
    protected void map(LongWritable k, Text line, Context ctx) throws IOException, InterruptedException {
      String cat = category.get(line.toString().split(",")[3]);
      if (cat == null) { ctx.getCounter(Join.ORDERS_WITHOUT_MENU).increment(1); return; }
      ctx.getCounter(Join.ORDERS_JOINED).increment(1);
      out.set(line + "," + cat);
      ctx.write(out, NullWritable.get());
    }
  }

  public static void main(String[] args) throws Exception {
    Configuration conf = new Configuration();
    String[] rest = new GenericOptionsParser(conf, args).getRemainingArgs();   // orders menu out
    Job job = Job.getInstance(conf, "map-side join");
    job.setJarByClass(JoinMapSide.class);
    job.addCacheFile(new URI(rest[1] + "#menu"));     // ship the menu to every task, linked as ./menu
    job.setMapperClass(JoinMapper.class);
    job.setNumReduceTasks(0);                         // no reducer, so no shuffle at all
    job.setOutputKeyClass(Text.class);
    job.setOutputValueClass(NullWritable.class);
    FileInputFormat.addInputPath(job, new Path(rest[0]));
    FileOutputFormat.setOutputPath(job, new Path(rest[2]));
    System.exit(job.waitForCompletion(true) ? 0 : 1);
  }
}
