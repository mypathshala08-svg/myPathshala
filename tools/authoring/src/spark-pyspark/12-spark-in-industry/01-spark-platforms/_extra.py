def _sec(i,h,inner): return f'\n<section class="part" id="{i}"><span class="part-label"><b>+</b> Going deeper</span><h2>{h}</h2>\n{inner}\n</section>\n'
def _cap(f,a=None,b=None):
    s=open(os.path.join(HERE,'..','..','lab','captures',f),encoding='utf-8').read()
    if a: s=s[s.index(a):]
    if b and b in s: s=s[:s.index(b)]
    return s.rstrip()
EXTRA=_sec('industries','Industry use cases and project ideas',
table(['Industry','Spark use','Course lesson'],[['Food delivery / e-commerce','Order ETL, daily revenue','Modules 5–7'],['Banking','Fraud features, streaming alerts','Module 9'],['Retail','Customer segments (KMeans), basket (FPGrowth)','10.4'],['Media','Recommendations (ALS)','10.4'],['Social / telecom','Graph PageRank, communities','12.4']],minw=320)+
'<h3>Project ideas</h3>'+table(['Project','Skills'],[['Daily sales lakehouse','Parquet/Delta, partitions, jobs'],['Live order dashboard','Structured Streaming + Kafka'],['Dish recommender','ALS, cold-start handling'],['Referral graph','GraphFrames PageRank, components']],minw=320))
