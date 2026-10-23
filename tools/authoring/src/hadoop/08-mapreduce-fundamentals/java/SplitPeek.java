// SplitPeek.java: a map-only job that reports, for every input split, where it starts,
// how long it is, which hosts hold it, the first and last record offsets, and the record count.
import java.io.IOException;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.input.FileSplit;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.util.GenericOptionsParser;

public class SplitPeek {
  public static class PeekMapper extends Mapper<LongWritable, Text, NullWritable, Text> {
    private long first = -1, last = -1, records = 0;
    private String lastLine = "";

    @Override
    protected void map(LongWritable offset, Text line, Context ctx) {
      if (first < 0) first = offset.get();
      last = offset.get();
      lastLine = line.toString();
      records++;
    }

    @Override
    protected void cleanup(Context ctx) throws IOException, InterruptedException {
      FileSplit s = (FileSplit) ctx.getInputSplit();
      String host = java.net.InetAddress.getLocalHost().getHostName();
      ctx.write(NullWritable.get(), new Text(String.format(
          "split start=%d length=%d | records=%d first_offset=%d last_offset=%d last_line=%s | ran_on=%s",
          s.getStart(), s.getLength(), records, first, last, lastLine, host)));
    }
  }

  public static void main(String[] args) throws Exception {
    Configuration conf = new Configuration();
    String[] rest = new GenericOptionsParser(conf, args).getRemainingArgs();
    Job job = Job.getInstance(conf, "split peek");
    job.setJarByClass(SplitPeek.class);
    job.setMapperClass(PeekMapper.class);
    job.setNumReduceTasks(0);                     // map-only: one output file per map task
    job.setOutputKeyClass(NullWritable.class);
    job.setOutputValueClass(Text.class);
    FileInputFormat.addInputPath(job, new Path(rest[0]));
    FileOutputFormat.setOutputPath(job, new Path(rest[1]));
    System.exit(job.waitForCompletion(true) ? 0 : 1);
  }
}
