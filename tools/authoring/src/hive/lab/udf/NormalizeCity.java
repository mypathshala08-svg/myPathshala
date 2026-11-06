package in.myphatshala.hive;

import java.util.Map;
import org.apache.hadoop.hive.ql.exec.Description;
import org.apache.hadoop.hive.ql.exec.UDFArgumentException;
import org.apache.hadoop.hive.ql.metadata.HiveException;
import org.apache.hadoop.hive.ql.udf.generic.GenericUDF;
import org.apache.hadoop.hive.serde2.objectinspector.ObjectInspector;
import org.apache.hadoop.hive.serde2.objectinspector.PrimitiveObjectInspector;
import org.apache.hadoop.hive.serde2.objectinspector.primitive.PrimitiveObjectInspectorFactory;
import org.apache.hadoop.hive.serde2.objectinspector.primitive.PrimitiveObjectInspectorUtils;

@Description(name = "normalize_city",
    value = "_FUNC_(str) - trims, title-cases and maps old city names (Bombay -> Mumbai)",
    extended = "Example: SELECT _FUNC_('  bombay ') returns 'Mumbai'")
public class NormalizeCity extends GenericUDF {
  private static final Map<String, String> OLD = Map.of(
      "bombay", "Mumbai", "bangalore", "Bengaluru", "madras", "Chennai",
      "calcutta", "Kolkata", "poona", "Pune", "gurgaon", "Gurugram");
  private PrimitiveObjectInspector in;

  @Override
  public ObjectInspector initialize(ObjectInspector[] args) throws UDFArgumentException {
    if (args.length != 1 || args[0].getCategory() != ObjectInspector.Category.PRIMITIVE)
      throw new UDFArgumentException("normalize_city takes exactly one string argument");
    in = (PrimitiveObjectInspector) args[0];
    return PrimitiveObjectInspectorFactory.javaStringObjectInspector;
  }

  @Override
  public Object evaluate(DeferredObject[] args) throws HiveException {
    Object v = args[0].get();
    if (v == null) return null;
    String s = PrimitiveObjectInspectorUtils.getString(v, in).trim().replaceAll("\\s+", " ");
    if (s.isEmpty()) return null;
    String mapped = OLD.get(s.toLowerCase());
    if (mapped != null) return mapped;
    StringBuilder b = new StringBuilder();
    for (String w : s.toLowerCase().split(" "))
      b.append(b.length() > 0 ? " " : "").append(Character.toUpperCase(w.charAt(0))).append(w.substring(1));
    return b.toString();
  }

  @Override
  public String getDisplayString(String[] children) {
    return "normalize_city(" + children[0] + ")";
  }
}
