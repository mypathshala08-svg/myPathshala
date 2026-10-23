// WordCountCombiner.java: word count with an optional combiner.  -D wc.combiner=true|false
import java.io.IOException;
import java.util.StringTokenizer;
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

public class WordCountCombiner {
  public static class TokenizerMapper extends Mapper<LongWritable, Text, Text, IntWritable> {
    private static final IntWritable ONE = new IntWritable(1);
    private final Text word = new Text();
    @Override
    public void map(LongWritable k, Text line, Context ctx) throws IOException, InterruptedException {
      StringTokenizer it = new StringTokenizer(line.toString().toLowerCase(), " \t.,!?;:\"'()");
      while (it.hasMoreTokens()) { word.set(it.nextToken()); ctx.write(word, ONE); }
    }
  }

  // Used as the reducer AND (optionally) as the combiner: summing is safe to do in pieces.
  public static class IntSumReducer extends Reducer<Text, IntWritable, Text, IntWritable> {
    private final IntWritable result = new IntWritable();
    @Override
    public void reduce(Text word, Iterable<IntWritable> counts, Context ctx) throws IOException, InterruptedException {
      int sum = 0;
      for (IntWritable c : counts) sum += c.get();
      result.set(sum);
      ctx.write(word, result);
    }
  }

  public static void main(String[] args) throws Exception {
    Configuration conf = new Configuration();
    String[] rest = new GenericOptionsParser(conf, args).getRemainingArgs();
    Job job = Job.getInstance(conf, "word count combiner=" + conf.getBoolean("wc.combiner", true));
    job.setJarByClass(WordCountCombiner.class);
    job.setMapperClass(TokenizerMapper.class);
    if (conf.getBoolean("wc.combiner", true)) job.setCombinerClass(IntSumReducer.class);
    job.setReducerClass(IntSumReducer.class);
    job.setOutputKeyClass(Text.class);
    job.setOutputValueClass(IntWritable.class);
    FileInputFormat.addInputPath(job, new Path(rest[0]));
    FileOutputFormat.setOutputPath(job, new Path(rest[1]));
    System.exit(job.waitForCompletion(true) ? 0 : 1);
  }
}
