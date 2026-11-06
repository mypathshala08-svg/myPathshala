def _sec(i,h,inner): return f'\n<section class="part" id="{i}"><span class="part-label"><b>+</b> Going deeper</span><h2>{h}</h2>\n{inner}\n</section>\n'
def _cap(f,a=None,b=None):
    s=open(os.path.join(HERE,'..','..','lab','captures',f),encoding='utf-8').read()
    if a: s=s[s.index(a):]
    if b and b in s: s=s[:s.index(b)]
    return s.rstrip()
EXTRA=_sec('arrow-udfs','Arrow UDFs: five ways to run the same rule',
'<p>Ek hi rule (amount × 1.05), 3 million rows, paanch tareeke. Built-in sabse fast; Arrow-based UDFs pickle wale <code>@udf</code> se lagbhag 2× tez.</p>'+
code('python','arrow.py','from pyspark.sql.functions import arrow_udf\n@arrow_udf("double")\ndef gst(a):  # a is a pyarrow Int64Array\n    import pyarrow.compute as pc\n    return pc.multiply(a, 1.05)',_cap('l66_arrow.txt'))+
table(['API','Since','Input'],[['@udf (Arrow on by default)','4.0','row values'],['pandas_udf','2.3','pandas Series'],['arrow_udf','4.1','pyarrow Array'],['arrow_udtf','4.1','pyarrow batches'],['mapInArrow / applyInArrow','3.3 / 4.0','RecordBatch / Table']],minw=320))
