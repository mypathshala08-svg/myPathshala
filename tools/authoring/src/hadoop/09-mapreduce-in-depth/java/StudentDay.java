// StudentDay.java: a composite WritableComparable key (student, day) and a custom Writable value.
// Job: for every student and day, the number of orders, total spend and the biggest order.
import java.io.DataInput;
import java.io.DataOutput;
import java.io.IOException;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.io.Writable;
import org.apache.hadoop.io.WritableComparable;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.util.GenericOptionsParser;

public class StudentDay {

  /** Key: (student, day). Sorted by student, then day. */
  public static class StudentDayKey implements WritableComparable<StudentDayKey> {
    private String student = "";
    private String day = "";
    public StudentDayKey() { }                                   // Hadoop needs a no-argument constructor
    public void set(String s, String d) { student = s; day = d; }
    @Override public void write(DataOutput out) throws IOException { out.writeUTF(student); out.writeUTF(day); }
    @Override public void readFields(DataInput in) throws IOException { student = in.readUTF(); day = in.readUTF(); }
    @Override public int compareTo(StudentDayKey o) {
      int c = student.compareTo(o.student);
      return c != 0 ? c : day.compareTo(o.day);
    }
    @Override public int hashCode() { return student.hashCode() * 31 + day.hashCode(); }   // used by HashPartitioner
    @Override public boolean equals(Object o) {
      return o instanceof StudentDayKey && compareTo((StudentDayKey) o) == 0;
    }
    @Override public String toString() { return student + "\t" + day; }
  }

  /** Value: orders, total and max amount. Small and fixed size: 3 numbers. */
  public static class SpendWritable implements Writable {
    private int orders; private long total; private int max;
    public SpendWritable() { }
    public void set(int o, long t, int m) { orders = o; total = t; max = m; }
    @Override public void write(DataOutput out) throws IOException { out.writeInt(orders); out.writeLong(total); out.writeInt(max); }
    @Override public void readFields(DataInput in) throws IOException { orders = in.readInt(); total = in.readLong(); max = in.readInt(); }
    @Override public String toString() { return orders + "\t" + total + "\t" + max; }
  }

  public static class M extends Mapper<LongWritable, Text, StudentDayKey, SpendWritable> {
    private final StudentDayKey key = new StudentDayKey();
    private final SpendWritable val = new SpendWritable();
    @Override
    protected void map(LongWritable k, Text line, Context ctx) throws IOException, InterruptedException {
      String[] f = line.toString().split(",");        // order_id,student_id,time,item,amount
      int amount = Integer.parseInt(f[4]);
      key.set(f[1], f[2].substring(0, 10));          // "2026-09-20 08:36" -> "2026-09-20"
      val.set(1, amount, amount);
      ctx.write(key, val);
    }
  }

  public static class R extends Reducer<StudentDayKey, SpendWritable, StudentDayKey, SpendWritable> {
    private final SpendWritable out = new SpendWritable();
    @Override
    protected void reduce(StudentDayKey k, Iterable<SpendWritable> vals, Context ctx) throws IOException, InterruptedException {
      int orders = 0, max = 0; long total = 0;
      for (SpendWritable v : vals) { orders += v.orders; total += v.total; max = Math.max(max, v.max); }
      out.set(orders, total, max);
      ctx.write(k, out);
    }
  }

  public static void main(String[] args) throws Exception {
    Configuration conf = new Configuration();
    String[] rest = new GenericOptionsParser(conf, args).getRemainingArgs();
    Job job = Job.getInstance(conf, "student day");
    job.setJarByClass(StudentDay.class);
    job.setMapperClass(M.class);
    job.setCombinerClass(R.class);                    // orders, total and max are all safe to combine
    job.setReducerClass(R.class);
    job.setOutputKeyClass(StudentDayKey.class);
    job.setOutputValueClass(SpendWritable.class);
    FileInputFormat.addInputPath(job, new Path(rest[0]));
    FileOutputFormat.setOutputPath(job, new Path(rest[1]));
    System.exit(job.waitForCompletion(true) ? 0 : 1);
  }
}
