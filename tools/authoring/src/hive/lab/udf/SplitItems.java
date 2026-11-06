package in.myphatshala.hive;

import java.util.ArrayList;
import java.util.List;
import org.apache.hadoop.hive.ql.exec.Description;
import org.apache.hadoop.hive.ql.exec.UDFArgumentException;
import org.apache.hadoop.hive.ql.metadata.HiveException;
import org.apache.hadoop.hive.ql.udf.generic.GenericUDTF;
import org.apache.hadoop.hive.serde2.objectinspector.ObjectInspector;
import org.apache.hadoop.hive.serde2.objectinspector.ObjectInspectorFactory;
import org.apache.hadoop.hive.serde2.objectinspector.PrimitiveObjectInspector;
import org.apache.hadoop.hive.serde2.objectinspector.StructField;
import org.apache.hadoop.hive.serde2.objectinspector.StructObjectInspector;
import org.apache.hadoop.hive.serde2.objectinspector.primitive.PrimitiveObjectInspectorFactory;
import org.apache.hadoop.hive.serde2.objectinspector.primitive.PrimitiveObjectInspectorUtils;

@Description(name = "split_items",
    value = "_FUNC_(str) - turns 'dal:2,roti:4' into rows (item STRING, qty INT)")
public class SplitItems extends GenericUDTF {
  private PrimitiveObjectInspector in;
  private final Object[] out = new Object[2];

  @Override
  public StructObjectInspector initialize(StructObjectInspector argOIs) throws UDFArgumentException {
    List<? extends StructField> f = argOIs.getAllStructFieldRefs();
    ObjectInspector[] args = new ObjectInspector[f.size()];
    for (int i = 0; i < args.length; i++) args[i] = f.get(i).getFieldObjectInspector();
    return initialize(args);
  }

  @Override   // some Hive 4 code paths call this older entry point directly
  public StructObjectInspector initialize(ObjectInspector[] args) throws UDFArgumentException {
    if (args.length != 1) throw new UDFArgumentException("split_items takes exactly one argument");
    in = (PrimitiveObjectInspector) args[0];
    List<String> names = new ArrayList<>(List.of("item", "qty"));
    List<ObjectInspector> ois = new ArrayList<>(List.of(
        PrimitiveObjectInspectorFactory.javaStringObjectInspector,
        PrimitiveObjectInspectorFactory.javaIntObjectInspector));
    return ObjectInspectorFactory.getStandardStructObjectInspector(names, ois);
  }

  @Override
  public void process(Object[] args) throws HiveException {
    if (args[0] == null) return;
    String s = PrimitiveObjectInspectorUtils.getString(args[0], in);
    for (String part : s.split(",")) {
      String[] kv = part.trim().split(":");
      if (kv.length != 2 || kv[0].isEmpty()) continue;          // skip malformed entries
      out[0] = kv[0].trim();
      try { out[1] = Integer.parseInt(kv[1].trim()); } catch (NumberFormatException e) { out[1] = null; }
      forward(out);
    }
  }

  @Override
  public void close() throws HiveException { }
}
