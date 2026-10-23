// CodecBench.java: compress and decompress one local file with each Hadoop codec, single thread.
// Usage: hadoop CodecBench <file>
import java.io.*;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.io.IOUtils;
import org.apache.hadoop.io.compress.*;
import org.apache.hadoop.util.ReflectionUtils;

public class CodecBench {
  public static void main(String[] args) throws Exception {
    Configuration conf = new Configuration();
    File in = new File(args[0]);
    Class<?>[] codecs = {DefaultCodec.class, GzipCodec.class, BZip2Codec.class, SnappyCodec.class, Lz4Codec.class, ZStandardCodec.class};
    System.out.printf("%-14s %12s %7s %10s %10s %11s%n", "codec", "bytes", "ratio", "compress", "decompress", "splittable");
    System.out.printf("%-14s %,12d %7s%n", "(original)", in.length(), "100%");
    for (Class<?> c : codecs) {
      CompressionCodec codec = (CompressionCodec) ReflectionUtils.newInstance(c, conf);
      File out = new File(in.getPath() + codec.getDefaultExtension());
      long t0 = System.nanoTime();
      try (InputStream is = new FileInputStream(in); OutputStream os = codec.createOutputStream(new FileOutputStream(out))) {
        IOUtils.copyBytes(is, os, 1 << 16);
      }
      long t1 = System.nanoTime();
      try (InputStream is = codec.createInputStream(new FileInputStream(out)); OutputStream os = OutputStream.nullOutputStream()) {
        IOUtils.copyBytes(is, os, 1 << 16);
      }
      long t2 = System.nanoTime();
      System.out.printf("%-14s %,12d %6.1f%% %8.1f s %8.1f s %11s%n", codec.getDefaultExtension(), out.length(),
          100.0 * out.length() / in.length(), (t1 - t0) / 1e9, (t2 - t1) / 1e9,
          codec instanceof SplittableCompressionCodec ? "yes" : "no");
    }
  }
}
