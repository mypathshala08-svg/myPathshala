# run from E:\myPhatshala :  python tools/authoring/_xfer/add_lessons.py  then  node tools/build-manifest.js
import json
p='courses/spark-pyspark/course.json'; c=json.load(open(p,encoding='utf-8'))
add={'04-dataframes':('07-statistics-and-sampling','Statistics and sampling'),'10-mllib':('05-regression-models','Regression models'),'12-spark-in-industry':('05-pandas-api-on-spark','pandas API on Spark')}
for m in c['modules']:
    if m['slug'] in add:
        s,t=add[m['slug']]
        if all(l['slug']!=s for l in m['lessons']): m['lessons'].append({'slug':s,'title':t}); m['lessons'].sort(key=lambda l:l['slug'])
json.dump(c,open(p,'w',encoding='utf-8'),ensure_ascii=False,indent=2)
print('lessons:',sum(len(m['lessons']) for m in c['modules']))
