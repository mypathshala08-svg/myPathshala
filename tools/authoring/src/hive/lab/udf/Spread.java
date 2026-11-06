package in.myphatshala.hive;

import org.apache.hadoop.hive.ql.exec.Description;
import org.apache.hadoop.hive.ql.exec.UDFArgumentTypeException;
import org.apache.hadoop.hive.ql.metadata.HiveException;
import org.apache.hadoop.hive.ql.parse.SemanticException;
import org.apache.hadoop.hive.ql.udf.generic.AbstractGenericUDAFResolver;
import org.apache.hadoop.hive.ql.udf.generic.GenericUDAFEvaluator;
import org.apache.hadoop.hive.serde2.io.DoubleWritable;
import org.apache.hadoop.hive.serde2.objectinspector.ObjectInspector;
import org.apache.hadoop.hive.serde2.objectinspector.ObjectInspectorFactory;
import org.apache.hadoop.hive.serde2.objectinspector.PrimitiveObjectInspector;
import org.apache.hadoop.hive.serde2.objectinspector.StructField;
import org.apache.hadoop.hive.serde2.objectinspector.StructObjectInspector;
import org.apache.hadoop.hive.serde2.objectinspector.primitive.PrimitiveObjectInspectorFactory;
import org.apache.hadoop.hive.serde2.objectinspector.primitive.PrimitiveObjectInspectorUtils;
import org.apache.hadoop.hive.serde2.typeinfo.TypeInfo;
import java.util.Arrays;

@Description(name = "spread", value = "_FUNC_(x) - max(x) - min(x), ignoring NULLs")
public class Spread extends AbstractGenericUDAFResolver {
  @Override
  public GenericUDAFEvaluator getEvaluator(TypeInfo[] params) throws SemanticException {
    if (params.length != 1) throw new UDFArgumentTypeException(0, "spread takes one numeric argument");
    return new Eval();
  }

  public static class Eval extends GenericUDAFEvaluator {
    private PrimitiveObjectInspector inputOI;          // PARTIAL1, COMPLETE
    private StructObjectInspector partialOI;           // PARTIAL2, FINAL
    private StructField minF, maxF;

    static class Buf extends AbstractAggregationBuffer { double min, max; boolean empty = true; }

    @Override
    public ObjectInspector init(Mode m, ObjectInspector[] p) throws HiveException {
      super.init(m, p);
      if (m == Mode.PARTIAL1 || m == Mode.COMPLETE) inputOI = (PrimitiveObjectInspector) p[0];
      else { partialOI = (StructObjectInspector) p[0]; minF = partialOI.getStructFieldRef("min"); maxF = partialOI.getStructFieldRef("max"); }
      if (m == Mode.PARTIAL1 || m == Mode.PARTIAL2)
        return ObjectInspectorFactory.getStandardStructObjectInspector(Arrays.asList("min", "max"),
            Arrays.asList((ObjectInspector) PrimitiveObjectInspectorFactory.writableDoubleObjectInspector,
                          PrimitiveObjectInspectorFactory.writableDoubleObjectInspector));
      return PrimitiveObjectInspectorFactory.writableDoubleObjectInspector;
    }

    @Override public AggregationBuffer getNewAggregationBuffer() { return new Buf(); }
    @Override public void reset(AggregationBuffer b) { ((Buf) b).empty = true; }

    private void add(Buf b, double lo, double hi) {
      if (b.empty) { b.min = lo; b.max = hi; b.empty = false; }
      else { b.min = Math.min(b.min, lo); b.max = Math.max(b.max, hi); }
    }

    @Override public void iterate(AggregationBuffer b, Object[] p) {
      if (p[0] == null) return;
      double v = PrimitiveObjectInspectorUtils.getDouble(p[0], inputOI);
      add((Buf) b, v, v);
    }

    @Override public Object terminatePartial(AggregationBuffer ab) {
      Buf b = (Buf) ab;
      if (b.empty) return null;
      return new Object[] { new DoubleWritable(b.min), new DoubleWritable(b.max) };
    }

    @Override public void merge(AggregationBuffer b, Object partial) {
      if (partial == null) return;
      double lo = ((DoubleWritable) partialOI.getStructFieldData(partial, minF)).get();
      double hi = ((DoubleWritable) partialOI.getStructFieldData(partial, maxF)).get();
      add((Buf) b, lo, hi);
    }

    @Override public Object terminate(AggregationBuffer ab) {
      Buf b = (Buf) ab;
      return b.empty ? null : new DoubleWritable(b.max - b.min);
    }
  }
}
