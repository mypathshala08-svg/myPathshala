// BadPartitioner.java: a partitioner that returns a number outside 0..numReduceTasks-1 for one item
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Partitioner;

public class BadPartitioner extends Partitioner<Text, IntWritable> {
  @Override
  public int getPartition(Text item, IntWritable amount, int numReduceTasks) {
    return item.toString().length();                     // "vada pav" -> 8, but there are only 4 reducers
  }
}
