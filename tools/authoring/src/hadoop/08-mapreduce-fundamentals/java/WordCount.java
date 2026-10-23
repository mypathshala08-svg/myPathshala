// WordCount.java: the classic first MapReduce program (new org.apache.hadoop.mapreduce API).
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

public class WordCount {

  public static class TokenizerMapper extends Mapper<LongWritable, Text, Text, IntWritable> {
    private static final IntWritable ONE = new IntWritable(1);
    private final Text word = new Text();

    @Override
    public void map(LongWritable offset, Text line, Context context) throws IOException, InterruptedException {
      StringTokenizer it = new StringTokenizer(line.toString().toLowerCase(), " \t.,!?;:\"'()");
      while (it.hasMoreTokens()) {
        word.set(it.nextToken());
        context.write(word, ONE);                 // ("chai", 1)
      }
    }
  }

  public static class IntSumReducer extends Reducer<Text, IntWritable, Text, IntWritable> {
    private final IntWritable result = new IntWritable();

    @Override
    public void reduce(Text word, Iterable<IntWritable> ones, Context context) throws IOException, InterruptedException {
      int sum = 0;
      for (IntWritable one : ones) sum += one.get();
      result.set(sum);
      context.write(word, result);                // ("chai", 41873)
    }
  }

  public static void main(String[] args) throws Exception {
    Configuration conf = new Configuration();
    String[] rest = new GenericOptionsParser(conf, args).getRemainingArgs();
    if (rest.length != 2) { System.err.println("Usage: wordcount <in> <out>"); System.exit(2); }
    Job job = Job.getInstance(conf, "word count");
    job.setJarByClass(WordCount.class);
    job.setMapperClass(TokenizerMapper.class);
    job.setReducerClass(IntSumReducer.class);
    job.setOutputKeyClass(Text.class);
    job.setOutputValueClass(IntWritable.class);
    FileInputFormat.addInputPath(job, new Path(rest[0]));
    FileOutputFormat.setOutputPath(job, new Path(rest[1]));
    System.exit(job.waitForCompletion(true) ? 0 : 1);
  }
}
