def _sec(i,h,inner): return f'\n<section class="part" id="{i}"><span class="part-label"><b>+</b> Going deeper</span><h2>{h}</h2>\n{inner}\n</section>\n'
def _cap(f,a=None,b=None):
    s=open(os.path.join(HERE,'..','..','lab','captures',f),encoding='utf-8').read()
    if a: s=s[s.index(a):]
    if b and b in s: s=s[:s.index(b)]
    return s.rstrip()
EXTRA=_sec('all-levels','Every StorageLevel, side by side',
'<p>Lab mein humne PySpark 4.3 ke saare StorageLevel constants print kiye. Dhyaan do: PySpark mein koi <code>_SER</code> level nahi hai — Python data hamesha serialized hi store hota hai.</p>'+
code('python','levels.py','from pyspark import StorageLevel\ndf.persist(StorageLevel.MEMORY_AND_DISK_2)\nprint(df.storageLevel)\ncustom = StorageLevel(True, True, False, False, 3)',_cap('l31_levels.txt'))+
table(['Level','Kab use karein'],[['MEMORY_AND_DISK','Default for DataFrame; safe choice'],['MEMORY_ONLY','Chhota data, recompute sasta'],['DISK_ONLY','Bada data, memory tight'],['*_2 / *_3','Executor loss pe recompute avoid karna ho'],['OFF_HEAP','GC pressure kam karna ho (off-heap enable chahiye)']],minw=320))
