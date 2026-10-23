// FirstLastOrder.java: secondary sort. For every student: first order, last order and the
// longest gap between two orders, reading the orders in time order WITHOUT sorting in the reducer.
// Key = (student, time): sorted by both, partitioned and grouped by student only.
import java.io.DataInput;
import java.io.DataOutput;
import java.io.IOException;
import java.time.Duration;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.io.WritableComparable;
import org.apache.hadoop.io.WritableComparator;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Partitioner;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.util.GenericOptionsParser;

public class FirstLastOrder {

  public static class StudentTime implements WritableComparable<StudentTime> {
    String student = "", time = "";
    public StudentTime() { }
    @Override public void write(DataOutput out) throws IOException { out.writeUTF(student); out.writeUTF(time); }
    @Override public void readFields(DataInput in) throws IOException { student = in.readUTF(); time = in.readUTF(); }
    @Override public int compareTo(StudentTime o) {               // the SORT order: student, then time
      int c = student.compareTo(o.student);
      return c != 0 ? c : time.compareTo(o.time);
    }
    @Override public int hashCode() { return student.hashCode(); }
    @Override public boolean equals(Object o) { return o instanceof StudentTime && compareTo((StudentTime) o) == 0; }
  }

  // 1. Partition by student only, so all of a student's orders reach the same reducer
  public static class StudentPartitioner extends Partitioner<StudentTime, Text> {
    @Override public int getPartition(StudentTime k, Text v, int n) { return (k.student.hashCode() & Integer.MAX_VALUE) % n; }
  }

  // 2. Group by student only, so one reduce() call gets ALL of a student's orders (already time-sorted)
  public static class StudentGrouping extends WritableComparator {
    public StudentGrouping() { super(StudentTime.class, true); }
    @Override public int compare(WritableComparable a, WritableComparable b) {
      return ((StudentTime) a).student.compareTo(((StudentTime) b).student);
    }
  }

  public static class M extends Mapper<LongWritable, Text, StudentTime, Text> {
    private final StudentTime key = new StudentTime();
    private final Text val = new Text();
    @Override
    protected void map(LongWritable k, Text line, Context ctx) throws IOException, InterruptedException {
      String[] f = line.toString().split(",");          // order_id,student_id,time,item,amount
      key.student = f[1]; key.time = f[2];
      val.set(f[2] + " " + f[3]);
      ctx.write(key, val);
    }
  }

  public static class R extends Reducer<StudentTime, Text, Text, Text> {
    private static final DateTimeFormatter F = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm");
    private boolean sorted = true;
    @Override
    protected void reduce(StudentTime k, Iterable<Text> vals, Context ctx) throws IOException, InterruptedException {
      String first = null, last = null, prev = null, gapFrom = null, gapTo = null;
      long n = 0, maxGap = -1;
      for (Text v : vals) {                              // arrives in time order thanks to the sort
        String s = v.toString();
        if (first == null) first = s;
        if (prev != null) {
          if (s.substring(0, 16).compareTo(prev.substring(0, 16)) < 0) sorted = false;   // compare the time part only
          long gap = Duration.between(LocalDateTime.parse(prev.substring(0, 16), F), LocalDateTime.parse(s.substring(0, 16), F)).toMinutes();
          if (gap > maxGap) { maxGap = gap; gapFrom = prev.substring(0, 16); gapTo = s.substring(0, 16); }
        }
        prev = s; last = s; n++;
      }
      ctx.write(new Text(k.student), new Text(n + " orders | first " + first + " | last " + last
          + " | longest gap " + (maxGap / 60) + " h (" + gapFrom + " -> " + gapTo + ")"));
    }
    @Override
    protected void cleanup(Context ctx) { System.err.println("values were in time order in every group: " + sorted); }
  }

  public static void main(String[] args) throws Exception {
    Configuration conf = new Configuration();
    String[] rest = new GenericOptionsParser(conf, args).getRemainingArgs();
    Job job = Job.getInstance(conf, "first last order (secondary sort)");
    job.setJarByClass(FirstLastOrder.class);
    job.setMapperClass(M.class);
    job.setReducerClass(R.class);
    job.setPartitionerClass(StudentPartitioner.class);
    if (conf.getBoolean("ss.grouping", true)) job.setGroupingComparatorClass(StudentGrouping.class);
    job.setMapOutputKeyClass(StudentTime.class);
    job.setMapOutputValueClass(Text.class);
    job.setOutputKeyClass(Text.class);
    job.setOutputValueClass(Text.class);
    FileInputFormat.addInputPath(job, new Path(rest[0]));
    FileOutputFormat.setOutputPath(job, new Path(rest[1]));
    System.exit(job.waitForCompletion(true) ? 0 : 1);
  }
}
