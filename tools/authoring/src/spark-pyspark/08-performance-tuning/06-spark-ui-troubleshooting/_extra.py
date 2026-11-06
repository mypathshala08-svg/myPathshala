def _sec(i,h,inner): return f'\n<section class="part" id="{i}"><span class="part-label"><b>+</b> Going deeper</span><h2>{h}</h2>\n{inner}\n</section>\n'
def _cap(f,a=None,b=None):
    s=open(os.path.join(HERE,'..','..','lab','captures',f),encoding='utf-8').read()
    if a: s=s[s.index(a):]
    if b and b in s: s=s[:s.index(b)]
    return s.rstrip()
EXTRA=_sec('habits','Habits that keep the UI clean',
'<p>Kai UI problems code ki chhoti aadaton se aate hain. Lab ke real numbers:</p>'+
code('text','l116_clean.txt','# plan size and timing',_cap('l116_clean.txt','== 2)','== 5)'))+
table(['Symptom in UI','Habit','Fix'],[['Huge analysed plan, slow driver','withColumn in a loop','one select / withColumns'],['Long full-scan job for a check','count() &gt; 0','isEmpty()'],['Many rename Project nodes','chained withColumnRenamed','toDF(*cols)']],minw=320)+
'<p>Aur: <a href="../../11-spark-in-production/06-writing-clean-modular-pyspark/">11.6 Clean modular PySpark</a> · <a href="../07-profiling-and-tracking-from-code/">8.7 Profiling from code</a></p>')
